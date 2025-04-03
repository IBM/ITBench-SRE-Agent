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
import os
import time
from typing import Any, Dict, Optional, Type

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field

from lumyn.tools.linting.logql_linter import LogQLLinter
from lumyn.config.tools import NL2KubectlCustomToolInputPrompt, NL2KubectlCustomToolPrompt, NL2LogsSystemPrompt, NL2LogsPrompt

from .custom_function_definitions_grafana import fd_query_loki_logs
from .grafana_base_client import GrafanaBaseClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class NL2LogsCustomToolInput(BaseModel):
    nl_query: str = Field(
        title="NL Query",
        description=NL2KubectlCustomToolInputPrompt,
    )


class NL2LogsCustomTool(BaseTool, GrafanaBaseClient):
    name: str = "NL2Logs Tool"
    description: str = NL2KubectlCustomToolPrompt
    llm_backend: Any = None
    cache_function: bool = False
    args_schema: Type[BaseModel] = NL2LogsCustomToolInput

    def _run(self, nl_query: str) -> str:
        GrafanaBaseClient.model_post_init(self)
        try:
            function_name, function_arguments = self._generate_logql_query(
                prompt=nl_query)
            lint_message = LogQLLinter.lint(function_arguments)
            if lint_message != function_arguments:
                return lint_message
            return self._summarize_logs(self._query_loki_logs(**function_arguments))
        except Exception as exc:
            logger.error(f"NL2Logs Tool failed with: {exc}")
            return f"NL2Logs Tool failed with: {exc}"

    def _generate_logql_query(self, prompt: str) -> str:
        time_nano = time.time_ns()
        tools = [fd_query_loki_logs]
        function_name, function_arguments = self.llm_backend.inference(NL2LogsSystemPrompt, NL2LogsPrompt + prompt + f"\nHere is a dictionary of the values available for each label in the query {self._get_label_value_dict()} \n\nThe current time in nanoseconds is {time_nano}", tools)
        logger.info(f"NL2Logs Tool function arguments identified are: {function_name} {function_arguments}")
        print(f"NL2Logs Tool function arguments identified are: {function_name} {function_arguments}")
        return function_name, function_arguments

    def _query_loki_logs(
            self,
            query: str,
            limit: int = 10,
            start: Optional[str] = None,
            end: Optional[str] = None,
            since: Optional[str] = None,
            step: Optional[str] = None,
            interval: Optional[str] = None,
            direction: str = "backward") -> Optional[Dict[str, Any]]:
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/query_range"
            params = {
                "query": query,
                "limit": min(limit, 10),
                "start": start,
                "end": end,
                "since": since,
                "step": step,
                "interval": interval,
                "direction": direction
            }
            response = self._make_request("GET", url, params=params)
            logger.info(
                f"NL2Logs Tool query Loki logs: {response.status_code}")
            print(f"NL2Logs Tool query Loki logs: {response.content}")
            return response.json()
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)} Here is a dictionary of the values available for each label in the query {self._get_label_value_dict()}"
        
    def _get_labels(self):
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/labels"
            response = self._make_request("GET", url)
            return response.json()['data']
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"

    def _get_label_values(self, label):
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/label/{label}/values"
            response = self._make_request("GET", url)
            return response.json()['data']
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"
        
    def _get_app_label_values(self):
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/label/app/values"
            response = self._make_request("GET", url)
            return response.json()['data']
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"
        
    def _get_label_value_dict(self):
        try:
            datasource_id = self.get_datasource_id("loki")
            label_url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/labels"
            response = self._make_request("GET", label_url)
            label_value_dict = {}
            for label in response.json()['data']:
                value_url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/label/{label}/values"
                values = self._make_request("GET", value_url).json()['data']
                label_value_dict[label] = values
            return label_value_dict

        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"

    
    def _get_last_hour(self, application):
        try:
            datasource_id = self.get_datasource_id("loki")
            url = f"{self.grafana_url}/api/datasources/proxy/uid/{datasource_id}/loki/api/v1/query_range"
            params = {
                "query": f"app='{application}'",
            }
            response = self._make_request("GET", url, params=params)
            logger.info(f"NL2Logs Tool query Loki logs: {response.status_code}")
            print(f"NL2Logs Tool query Loki logs: {response.content}")
            return response.json()
        except Exception as e:
            print(f"Error querying Loki logs: {str(e)}")
            logger.error(f"Error querying Loki logs: {str(e)}")
            return f"Error querying Loki logs: {str(e)}"
        
    def _summarize_logs(self, logs):
        system_prompt = "You do log analysis and summarization. Look at the logs given to you and provide a brief summary and analysis of them."
        logs_summary = self.llm_backend.inference(system_prompt, json.dumps(logs))
        return logs_summary