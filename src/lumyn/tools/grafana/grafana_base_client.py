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


import logging
import os
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 120))
RETRY_TOTAL = int(os.getenv("RETRY_TOTAL", 3))
RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", 0.3))


class GrafanaBaseClient:
    grafana_url: Optional[str] = None
    topology_url: Optional[str] = None
    grafana_service_account_token: Optional[str] = None
    headers: Optional[Dict] = None
    session: Optional[Any] = None

    def model_post_init(self, __context):
        self.grafana_url = os.environ.get("GRAFANA_URL")
        self.topology_url = os.environ.get("TOPOLOGY_URL")
        self.grafana_service_account_token = os.environ.get(
            "GRAFANA_SERVICE_ACCOUNT_TOKEN")

        if not (self.grafana_url and self.grafana_service_account_token):
            raise ValueError(
                "(Grafana URL and Grafana service account token) or (Grafana URL, username and password) must be provided either through initialization parameters or configuration"
            )
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.grafana_service_account_token}"
        }
        self.session = self._create_retrying_session()

    def _create_retrying_session(self) -> requests.Session:
        session = requests.Session()

        retries = Retry(total=RETRY_TOTAL,
                        backoff_factor=RETRY_BACKOFF_FACTOR,
                        status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _make_request(self, method: str, url: str,
                      **kwargs) -> requests.Response:
        try:
            response = self.session.request(method,
                                            url,
                                            headers=self.headers,
                                            timeout=REQUEST_TIMEOUT,
                                            **kwargs)
            response.raise_for_status()
            return response
        except requests.Timeout:
            logger.error(f"Request timed out after {REQUEST_TIMEOUT} seconds")
            raise
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get_datasource_id(self, datasource_type: str) -> str:
        url = f"{self.grafana_url}/api/datasources"

        try:
            response = self._make_request("GET", url)
            datasources = response.json()

            for datasource in datasources:
                if datasource["type"] == datasource_type:
                    return datasource["uid"]
            raise ValueError(f"{datasource_type} data source not found")
        except Exception as e:
            logger.error(f"Error fetching datasources: {str(e)}")
            raise
