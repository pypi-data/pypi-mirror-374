"""
 Nexus Core.
"""

#  Copyright (c) 2023-2024. ECCO Sneaks & Data
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import asyncio
import os
import platform
import signal
import sys
import traceback
from typing import final, Type, Optional, Callable

import backoff
import urllib3.exceptions
from adapta.logs import LoggerInterface
from adapta.metrics import MetricsProvider
from adapta.process_communication import DataSocket
from adapta.storage.blob.base import StorageClient
from adapta.storage.query_enabled_store import QueryEnabledStore
from injector import Injector, Module, singleton

import esd_services_api_client.nexus.exceptions
from esd_services_api_client.crystal import (
    add_crystal_args,
    extract_crystal_args,
    CrystalConnector,
    AlgorithmRunResult,
    CrystalEntrypointArguments,
)
from esd_services_api_client.nexus.abstractions.logger_factory import (
    LoggerFactory,
    BootstrapLoggerFactory,
)
from esd_services_api_client.nexus.abstractions.metrics_provider_factory import (
    MetricsProviderFactory,
)
from esd_services_api_client.nexus.abstractions.nexus_object import AlgorithmResult
from esd_services_api_client.nexus.algorithms import (
    BaselineAlgorithm,
)
from esd_services_api_client.nexus.configurations.algorithm_configuration import (
    NexusConfiguration,
)
from esd_services_api_client.nexus.core.app_dependencies import (
    ServiceConfigurator,
)
from esd_services_api_client.nexus.core.serializers import (
    ResultSerializer,
)
from esd_services_api_client.nexus.input.input_processor import InputProcessor
from esd_services_api_client.nexus.input.input_reader import InputReader
from esd_services_api_client.nexus.input.payload_reader import (
    AlgorithmPayloadReader,
    AlgorithmPayload,
)
from esd_services_api_client.nexus.telemetry.recorder import TelemetryRecorder
from esd_services_api_client.nexus.telemetry.user_telemetry_recorder import (
    UserTelemetryRecorder,
)
from esd_services_api_client import __version__


def is_transient_exception(exception: Optional[BaseException]) -> Optional[bool]:
    """
    Check if the exception is retryable.
    """
    if not exception:
        return None
    match type(exception):
        case esd_services_api_client.nexus.exceptions.FatalNexusError:
            return False
        case esd_services_api_client.nexus.exceptions.TransientNexusError:
            return True
        case _:
            return False


async def graceful_shutdown():
    """
    Gracefully stops the event loop.
    """
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()

    asyncio.get_event_loop().stop()


def attach_signal_handlers():
    """
    Signal handlers for the event loop graceful shutdown.
    """
    if platform.system() != "Windows":
        asyncio.get_event_loop().add_signal_handler(
            signal.SIGTERM, lambda: asyncio.create_task(graceful_shutdown())
        )


@final
class Nexus:
    """
    Nexus is the object that manages everything related to running algorithms through Crystal.
    It takes care of result submission, signal handling, result recording, post-processing, metrics, logging etc.
    """

    def __init__(self, args: CrystalEntrypointArguments):
        self._configurator = ServiceConfigurator()
        self._injector: Optional[Injector] = None
        self._algorithm_class: Optional[Type[BaselineAlgorithm]] = None
        self._run_args = args
        self._algorithm_run_task: Optional[asyncio.Task] = None
        self._on_complete_tasks: list[type[UserTelemetryRecorder]] = []
        self._payload_types: list[type[AlgorithmPayload]] = []
        self._log_enricher: Callable[
            [
                AlgorithmPayload,
                CrystalEntrypointArguments,
            ],
            dict[str, dict[str, str]],
        ] | None = None
        self._log_tagger: Callable[
            [
                AlgorithmPayload,
                CrystalEntrypointArguments,
            ],
            dict[str, str],
        ] | None = None
        self._log_enrichment_delimiter: str = ", "

        self._metric_tagger: Callable[
            [
                AlgorithmPayload,
                CrystalEntrypointArguments,
            ],
            dict[str, str],
        ] | None = None

        attach_signal_handlers()

    @property
    def algorithm_class(self) -> Type[BaselineAlgorithm]:
        """
        Class of the algorithm used by this Nexus instance.
        """
        return self._algorithm_class

    def on_complete(self, *post_processors: type[UserTelemetryRecorder]) -> "Nexus":
        """
        Attaches a coroutine to run on algorithm completion.
        """
        self._on_complete_tasks.extend(post_processors)
        return self

    def add_reader(self, reader: Type[InputReader]) -> "Nexus":
        """
        Adds an input data reader for the algorithm.
        """
        self._configurator = self._configurator.with_input_reader(reader)
        return self

    def use_processor(self, input_processor: Type[InputProcessor]) -> "Nexus":
        """
        Initialises an input processor for the algorithm.
        """
        self._configurator = self._configurator.with_input_processor(input_processor)
        return self

    def use_algorithm(self, algorithm: Type[BaselineAlgorithm]) -> "Nexus":
        """
        Algorithm to use for this Nexus instance
        """
        self._algorithm_class = algorithm
        return self

    def inject_payload(self, *payload_types: Type[AlgorithmPayload]) -> "Nexus":
        """
        Adds payload types to inject to the DI container. Payloads will be deserialized at runtime.
        """
        self._payload_types = payload_types
        return self

    def inject_configuration(
        self, *configuration_types: Type[NexusConfiguration]
    ) -> "Nexus":
        """
        Adds custom configuration class instances to the DI container.
        """
        for config_type in configuration_types:
            self._configurator = self._configurator.with_configuration(
                config_type.from_environment()
            )

        return self

    def with_log_enricher(
        self,
        tagger: Callable[
            [
                AlgorithmPayload,
                CrystalEntrypointArguments,
            ],
            dict[str, str],
        ]
        | None,
        enricher: Callable[
            [
                AlgorithmPayload,
                CrystalEntrypointArguments,
            ],
            dict[str, dict[str, str]],
        ]
        | None = None,
        delimiter: str = ", ",
    ) -> "Nexus":
        """
        Adds a log `tagger` and a log `enricher` to be used with injected logger.
        A log `tagger` will add key-value tags to each emitted log message, and those tags can be inferred from the payload and entrypoint arguments.
        A log `enricher` will add additional static templated content to log messages, and render those templates using payload properties entrypoint argyments.
        """
        self._log_tagger = tagger
        self._log_enricher = enricher
        self._log_enrichment_delimiter = delimiter
        return self

    def with_metric_tagger(
        self,
        tagger: Callable[
            [
                AlgorithmPayload,
                CrystalEntrypointArguments,
            ],
            dict[str, str],
        ]
        | None = None,
    ) -> "Nexus":
        """
        Adds a metric `enricher` to be used with injected metrics provider to assign additional tags to emitted metrics.
        """
        self._metric_tagger = tagger
        return self

    def with_module(self, module: Type[Module]) -> "Nexus":
        """
        Adds a (custom) DI module into the DI container.
        """
        self._configurator = self._configurator.with_module(module)
        return self

    async def _submit_result(
        self,
        result: Optional[AlgorithmResult] = None,
        ex: Optional[BaseException] = None,
    ) -> None:
        @backoff.on_exception(
            wait_gen=backoff.expo,
            exception=(urllib3.exceptions.HTTPError,),
            max_time=10,
            raise_on_giveup=True,
        )
        def save_result(data: AlgorithmResult) -> str:
            """
            Saves blob and returns the uri

            :param: path: path to save the blob
            :param: output_consumer_df: Formatted dataframe into ECCO format
            :param: storage_client: Azure storage client

            :return: blob uri
            """
            result_ = data.result()
            serializer = self._injector.get(ResultSerializer)
            storage_client = self._injector.get(StorageClient)
            output_path = f"{os.getenv('NEXUS__ALGORITHM_OUTPUT_PATH')}/{self._run_args.request_id}.json"
            blob_path = DataSocket(
                data_path=output_path, alias="output", data_format="null"
            ).parse_data_path()
            storage_client.save_data_as_blob(
                data=result_,
                blob_path=blob_path,
                serialization_format=serializer.get_serialization_format(result_),
                overwrite=True,
            )
            return storage_client.get_blob_uri(blob_path=blob_path)

        receiver = self._injector.get(CrystalConnector)

        match is_transient_exception(ex):
            case None:
                receiver.submit_result(
                    result=AlgorithmRunResult(sas_uri=save_result(result)),
                    run_id=self._run_args.request_id,
                    algorithm=os.getenv("CRYSTAL__ALGORITHM_NAME"),
                    debug=os.getenv("IS_LOCAL_RUN") == "1",
                )
            case True:
                sys.exit(1)
            case False:
                receiver.submit_result(
                    result=AlgorithmRunResult(
                        message=f"{type(ex)}: {ex})", cause=traceback.format_exc()
                    ),
                    run_id=self._run_args.request_id,
                    algorithm=os.getenv("CRYSTAL__ALGORITHM_NAME"),
                    debug=os.getenv("IS_LOCAL_RUN") == "1",
                )
            case _:
                sys.exit(1)

    async def _get_payload(
        self, payload_type: type[AlgorithmPayload]
    ) -> AlgorithmPayload:
        async with AlgorithmPayloadReader(
            payload_uri=self._run_args.sas_uri,
            payload_type=payload_type,
        ) as reader:
            return reader.payload

    async def activate(self):
        """
        Activates the run sequence.
        """

        self._injector = Injector(self._configurator.injection_binds)

        bootstrap_logger: LoggerInterface = self._injector.get(
            BootstrapLoggerFactory
        ).create_logger(
            request_id=self._run_args.request_id,
            algorithm_name=os.getenv("CRYSTAL__ALGORITHM_NAME"),
        )

        bootstrap_logger.start()

        try:
            logger_fixed_template = {}
            logger_tags = {}
            metric_tags = {}

            for payload_type in self._payload_types:
                payload = await self._get_payload(payload_type=payload_type)
                self._injector.binder.bind(
                    payload.__class__, to=payload, scope=singleton
                )
                logger_fixed_template |= (
                    self._log_enricher(payload, self._run_args)
                    if self._log_enricher
                    else {}
                )
                logger_tags |= (
                    self._log_tagger(payload, self._run_args)
                    if self._log_tagger
                    else {}
                )
                metric_tags |= (
                    self._metric_tagger(payload, self._run_args)
                    if self._metric_tagger
                    else {}
                )

            logger_factory = LoggerFactory(
                fixed_template=logger_fixed_template,
                fixed_template_delimiter=self._log_enrichment_delimiter,
                global_tags=logger_tags,
            )
            # bind app-level LoggerFactory now
            self._injector.binder.bind(
                logger_factory.__class__,
                to=logger_factory,
                scope=singleton,
            )

            # bind app-level MetricsProvider now
            metrics_provider = MetricsProviderFactory(
                global_tags=metric_tags,
            ).create_provider()

            self._injector.binder.bind(
                MetricsProvider,
                to=metrics_provider,
                scope=singleton,
            )

        except BaseException as ex:  # pylint: disable=broad-except
            bootstrap_logger.error("Error reading algorithm payload", ex)

            # ensure we flush bootstrap logger before we exit
            bootstrap_logger.stop()
            sys.exit(1)

        bootstrap_logger.stop()

        root_logger: LoggerInterface = self._injector.get(LoggerFactory).create_logger(
            logger_type=self.__class__,
        )

        root_logger.start()

        algorithm: BaselineAlgorithm = self._injector.get(self._algorithm_class)
        telemetry_recorder: TelemetryRecorder = self._injector.get(TelemetryRecorder)

        root_logger.info(
            "Running algorithm {algorithm} on Nexus version {version}",
            algorithm=algorithm.__class__.alias().upper(),
            version=__version__,
        )

        async with algorithm as instance:
            self._algorithm_run_task = asyncio.create_task(
                instance.run(**self._run_args.__dict__)
            )

            # avoid exception propagation to main thread, since we need to handle it later
            await asyncio.wait(
                [self._algorithm_run_task], return_when=asyncio.FIRST_EXCEPTION
            )
            ex = self._algorithm_run_task.exception()

            if ex is not None:
                root_logger.error(
                    "Algorithm {algorithm} run failed on Nexus version {version}",
                    ex,
                    algorithm=algorithm.__class__.alias().upper(),
                    version=__version__,
                )
                metrics_provider.increment("failed_runs")
            else:
                metrics_provider.increment("successful_runs")

            await self._submit_result(
                self._algorithm_run_task.result() if not ex else None,
                self._algorithm_run_task.exception(),
            )

            # record telemetry
            root_logger.info(
                "Recording telemetry for the run {run_id}",
                run_id=self._run_args.request_id,
            )
            async with telemetry_recorder as recorder:
                await recorder.record(
                    run_id=self._run_args.request_id, **algorithm.inputs
                )
                on_complete_tasks = [
                    recorder.record_user_telemetry(
                        user_recorder=self._injector.get(on_complete_task_class),
                        run_id=self._run_args.request_id,
                        result=self._algorithm_run_task.result(),
                        **algorithm.inputs,
                    )
                    for on_complete_task_class in self._on_complete_tasks
                ]
                if len(on_complete_tasks) > 0:
                    done, pending = await asyncio.wait(
                        on_complete_tasks, return_when=asyncio.FIRST_EXCEPTION
                    )
                    if len(pending) > 0:
                        metrics_provider.increment("telemetry_reports_incomplete")
                        root_logger.warning(
                            "Some post-processing operations did not complete or failed. Please review application logs for more information"
                        )

                    for done_on_complete_task in done:
                        on_complete_task_exc = done_on_complete_task.exception()
                        if on_complete_task_exc:
                            metrics_provider.increment("telemetry_reports_failed")
                            root_logger.warning(
                                "Post processing task failed",
                                exception=on_complete_task_exc,
                            )
                        else:
                            metrics_provider.increment("telemetry_reports_succeeded")
                else:
                    root_logger.info(
                        "No post processing tasks were defined for this run."
                    )

            # dispose of QES instance gracefully as it might hold open connections
            qes = self._injector.get(QueryEnabledStore)
            qes.close()

        root_logger.stop()

    @classmethod
    def create(cls) -> "Nexus":
        """
        Creates a Nexus instance with Crystal CLI arguments parsed into input.
        """
        parser = add_crystal_args()
        return Nexus(extract_crystal_args(parser.parse_args()))
