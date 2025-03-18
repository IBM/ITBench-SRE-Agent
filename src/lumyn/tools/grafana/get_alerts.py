# Copyright contributors to the ITBench project. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
import logging
from typing import Any, Dict, Optional

from crewai.tools.base_tool import BaseTool

from .grafana_base_client import GrafanaBaseClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GetAlertsCustomTool(BaseTool, GrafanaBaseClient):
    name: str = "GetAlerts Tool"
    description: str = "Get alerts on the IT environment at present time via the Grafana API."

    def _run(self) -> str:
        GrafanaBaseClient.model_post_init(self)
        data = None
        try:
            url = f"{self.grafana_url}/api/prometheus/grafana/api/v1/alerts"
            response = self._make_request("GET", url)
            logger.info(f"GetAlertsCustomTool: {response.status_code}")
            logger.info(f"GetAlertsCustomTool: {response.content}")
            print(f"GetAlertsCustomTool: {response.status_code}")
            print(f"GetAlertsCustomTool: {response.content}")
            data = response.json()
            if response.status_code == 200:
                if len(data["data"]["alerts"]) == 0:
                    return None
                alerts = list(filter(lambda i: i["state"] == "Alerting", data["data"]["alerts"]))
                return alerts
            return None
        except Exception as e:
            print(f"Error querying Grafana Alerts API: {str(e)}")
            logger.error(f"Error querying Grafana Alerts API: {str(e)}")
            return None
 