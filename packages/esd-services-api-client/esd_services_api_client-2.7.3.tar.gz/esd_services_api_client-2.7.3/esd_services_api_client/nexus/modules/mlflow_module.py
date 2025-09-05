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

"""
MLFlow module that provides the MLFlow client to the Nexus framework.
"""

import os
from typing import final
from injector import Module, singleton, provider
from adapta.ml.mlflow import MlflowBasicClient
from esd_services_api_client.nexus.exceptions.startup_error import (
    FatalStartupConfigurationError,
)


@final
class MlflowModule(Module):
    """
    MLFlow module.
    """

    @singleton
    @provider
    def provide(self) -> MlflowBasicClient:
        """
        DI factory method.
        """
        if "NEXUS__MLFLOW_TRACKING_URI" not in os.environ:
            raise FatalStartupConfigurationError("NEXUS__MLFLOW_TRACKING_URI")
        return MlflowBasicClient(os.environ["NEXUS__MLFLOW_TRACKING_URI"])
