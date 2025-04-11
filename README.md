# Running with Docker
The agent should always be run in a container in order to prevent harmful commands being run on the user's PC.  

1. Clone the repo.
```bash
git clone git@github.com:IBM/itbench-sre-agent.git
cd itbench-sre-agent
```

2. Move the kubeconfig of the cluster on which ITBench is running into the root directory of this repo.

3. Create a `.env` based on `.env.tmpl` by running:
```bash
cp .env.tmpl .env
```
.env guide:
```python
### Embedding (used to enable CrewAI memory feature - Optional) ### 
MODEL_EMBEDDING="" # embedding model name, e.g. text-embedding-3-large
URL_EMBEDDING="" # embedding model url, e.g. https://xxxxx.azure-api.net/openai/deployments/text-embedding-3-large-1/embeddings?api-version=2023-05-15
API_VERSION_EMBEDDING="" # embedding model api version, e.g. 2023-05-15 (same as the end of the url)

### Agent - configures that backend used by the agent ### 
PROVIDER_AGENTS="" # agent model provider, e.g. watsonx, azure, anthropic, openai
MODEL_AGENTS="" # agent model or checkpoint name, e.g. ibm/granite-3-2-8b-instruct, gpt-4o, gpt-4o-2024-11-20
URL_AGENTS="" # agent model url, e.g. https://us-south.ml.cloud.ibm.com (no url required for openai)
API_VERSION_AGENTS="" # only required for azure, e.g. 2024-12-01-preview
API_KEY_AGENTS="" # agent api key
REASONING_EFFORT_AGENTS="" # for o1, o1-mini, and o3-mini only, e.g. low, medium, high
SEED_AGENTS=10 # sets the seed for the agent model
TOP_P_AGENTS=0.95 # sets the top p for the agent model
TEMPERATURE_AGENTS=0.0 # sets the temperature for the agent model
THINKING_AGENTS="" # for Claude Sonnet 3.7 and Granite 3.2 only. use anthropic for CS3.7 and wx for G3.2. leave empty to use these models without thinking
THINKING_BUDGET_AGENTS=6000 # for Claude Sonnet 3.7 only. determines the number of thinking token allowed
MAX_TOKENS_AGENTS=16000 # max new tokens the agent model can output per call

### Tools - configures that backend used by the tools ###
PROVIDER_TOOLS="" # see above
MODEL_TOOLS="" # see above
URL_TOOLS="" # see above
API_VERSION_TOOLS="" # see above
API_KEY_TOOLS="" # see above
REASONING_EFFORT_TOOLS="" # see above
SEED_TOOLS=10 # see above
TOP_P_TOOLS=0.95 # see above
TEMPERATURE_TOOLS=0.0 # see above
THINKING_TOOLS="" # see above
THINKING_BUDGET_TOOLS=6000 # see above
MAX_TOKENS_TOOLS=16000 # see above

WX_PROJECT_ID="" # required only when using a watsonx model

# Linux
OBSERVABILITY_STACK_URL="http://localhost:8080/grafana"
TOPOLOGY_URL="http://localhost:8081"

# Mac
OBSERVABILITY_STACK_URL="http://docker.host.internal:8080/grafana"
TOPOLOGY_URL="http://docker.host.internal:8081"

# DO NOT ALTER THESE VALUES
AGENT_TASK_DIRECTORY="config"
SRE_AGENT_EVALUATION_DIRECTORY="/app/lumyn/outputs"
STRUCTURED_UNSTRUCTURED_OUTPUT_DIRECTORY_PATH="/app/lumyn/outputs"
SRE_AGENT_NAME_VERSION_NUMBER="Test"
EXP_NAME="Test"
GOD_MODE="True"
OBSERVABILITY_STACK_SERVICE_ACCOUNT_TOKEN="not_required"
KUBECONFIG="/app/lumyn/config"
```

Update the values here to switch LLM backends. Supports all providers and models that are available through [LiteLLM](https://docs.litellm.ai/docs/providers). Also update the values at the bottom so the agent can interact with your cluster.

4. Build the image.
```bash
docker build -t itbench-sre-agent .
```

5. Run the image in interactive mode:
```bash
# Linux
docker run --network=host -it itbench-sre-agent /bin/bash

# Mac
docker run -it itbench-sre-agent /bin/bash
```
6. Start the agent:
```bash
crewai run
```

Pre-built images coming soon.

# Development Setup Instructions
1. Clone the repo
```bash
git clone git@github.com:IBM/itbench-sre-agent.git
cd itbench-sre-agent
```

2. This project uses Python 3.12. Install uv for dependecy management and install crewai.  

Mac/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install crewai
```
  
Windows  
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install crewai
```
3. Navigate to the root project directory and install the dependencies using the CLI command:
```bash
crewai install
```
  
4. Create a `.env` based on `.env.tmpl` by running:
```bash
cp .env.tmpl .env
```
Update the values here to switch LLM backends.
  
5. Customize:  
- Modify `src/lumyn/config/agents.yaml` to define your agents
- Modify `src/lumyn/config/tasks.yaml` to define your tasks
- Modify `src/lumyn/crew.py` to add your own logic, tools and specific args
- Modify `src/lumyn/main.py` to add custom inputs for your agents and tasks

# User Interface
To leverage Panel as a UI, head over to the ui directory (via cd ui) and run:

`panel serve panel_main.py --show`

and then head over to http://localhost:5006/panel_main in your browser. Tested in Firefox and Chrome.

To leverage Streamlit as a UI, head over to the ui directory (via cd ui) and run:

`streamlit run streamlit_main.py`

and then head over to http://localhost:5006/panel_main in your browser. Tested in Firefox and Chrome.
