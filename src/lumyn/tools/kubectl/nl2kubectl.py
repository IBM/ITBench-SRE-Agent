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
import re
import subprocess
from typing import Any, Dict, Optional, Type

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from lumyn.tools.linting.kubectl_linter import KubectlLinter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class NL2KubectlCustomToolInput(BaseModel):
    nl_query: str = Field(
        title="NL Query",
        description="NL query to execute. Keep queries simple and straight-forward.\
        This tool cannot handle complex mutli-step queries.\
        Make sure to include a namespace where required.",
    )


class NL2KubectlCustomTool(BaseTool):
    name: str = "NL2Kubectl Tool"
    description: str = (
        "Converts natural language to kubectl commands and executes them. Can be used to get/describe/edit Kubernetes deployments, services, and other Kubernetes components. Only takes one query at a time. Keep queries simple and straight-forward. This tool cannot handle complex mutli-step queries. Remember that most kubectl queries require a namespace name."
    )
    llm_backend: Any
    is_remediation: bool = False
    god_mode: bool = False
    args_schema: Type[BaseModel] = NL2KubectlCustomToolInput

    def _run(self, nl_query: str) -> str:
        harmful_commands = ["rm "]
        if self.is_remediation:
            while True:
                try:
                    command = self._generate_kubectl_command(prompt=nl_query)
                    print(command)
                    user_input = input("Execute command? (Y/N)").strip().lower()
                    
                    while user_input not in ["y", "n"]:
                        print("Please enter 'Y' or 'N'.")
                        user_input = input("Execute command? (Y/N)").strip().lower()
                    
                    if user_input == "y":
                        return self._execute_kubectl_command(command)[0:8000]
                    else:
                        problem_description = input("What is wrong with the command?")
                        nl_query = (
                            f"User says there is a problem with the command that you wrote:\n"
                            f"{command}\nHere is their description of the problem: {problem_description}"
                        )
                except Exception as exc:
                    logger.error(f"NL2Kubectl Tool failed with: {exc}")
                    return f"NL2Kubectl Tool failed with: {exc}"
        else:
            try:
                    command = self._generate_kubectl_command(prompt=nl_query)
                    for harmful_command in harmful_commands:
                        if command.startswith(harmful_command):
                            return "Potentially harmful command found. Execution is not allowed."
                    return self._execute_kubectl_command(command)[0:8000]
            except Exception as exc:
                    logger.error(f"NL2Kubectl Tool failed with: {exc}")
                    return f"NL2Kubectl Tool failed with: {exc}"

    def _generate_kubectl_command(self, prompt: str) -> str:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "in_context_examples", "kubectl.txt"),
                  "r") as f:
            kubectl_icl = f.read()

        system_prompt = f"{kubectl_icl} You write kubectl commands. Answer with only the correct kubectl command. The formatting should always be like this: ```bash\n<kubectl command>\n```"

        response = self.llm_backend.inference(system_prompt, prompt)
        command_of_interest = re.search(r'```bash\n(.*?)\n```', response, re.DOTALL).group(1).strip()
        logger.info(f"NL2Kubectl Tool NL prompt received: {prompt}")
        logger.info(f"NL2Kubectl Tool response received: {response}")
        logger.info(f"NL2Kubectl Tool command returned: {command_of_interest}")
        print(f"NL2Kubectl Tool NL prompt received: {prompt}")
        print(f"NL2Kubectl Tool NL response received: {response}")
        print(f"NL2Kubectl Tool command returned: {command_of_interest}")
        return command_of_interest

    def _execute_kubectl_command(self, command: str): #-> Optional[Dict[str, Any]]:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"NL2Kubectl Tool command execution: {result.stdout}")
            print(f"NL2Kubectl Tool command execution: {result.stdout}")
            return result.stdout
        else:
            print(f"Error executing kubectl command: {result.stderr}")
            logger.error(f"Error executing kubectl command: {result.stderr}")
            return f"Error executing kubectl command: {result.stderr}"
        
    def _summarize_kubernetes(self, kubernetes):
        system_prompt = "You do kubectl output analysis and summarization. Look at the kubectl output given to you and provide a brief summary and analysis of them."
        kubernetes_summary = self.llm_backend.inference(system_prompt, kubernetes)
        return kubernetes_summary
