# Participating in the ITBench Leaderboard

## Prerequisite(s)
1. Podman (or Docker)
   
## Getting Started (for agents based on ITBench-SRE-Agent -- this repository)
1. Follow the instructions [here](https://github.com/IBM/ITBench-Leaderboard) to create an agent record.

2. Verify that an `agent-manifest.json` exists is uploaded to the private repository created as a part of the previous step.

3. Clone your private repository and make note of the absolute path to the `agent-manifest.json` uploaded there-in.

3. Clone this repo and `cd` into it
```bash
git clone git@github.com:IBM/ITBench-SRE-Agent.git  
cd ITBench-SRE-Agent  
```  
  
4. Update the environment variables as recommended in the [README][./README.md]
```bash
cp .env.tmpl .env  
vi .env
```  
  
5. Build sre-agent-harness image by running
```bash
podman build -f sre-agent-harness.Dockerfile -t sre-agent-harness:latest .
```

6. Run the agent harness and the underlying agent by running
```bash
podman run --rm -it --name sre-agent-harness \
    --mount type=bind,src=<ABSOLUTE_PATH_TO_agent-manifest.json>,dst=/tmp/agent-manifest.json \
    --mount type=bind,src=<ABSOLUTE_PATH_TO_THE_DOT_ENV>/.env,dst=/etc/lumyn/.env \
    localhost/sre-agent-harness:latest \
    --host itbench.apps.prod.itbench.res.ibm.com \
    --benchmark_timeout 60000
```

7. The agent harness interacts with the ITBench Leaderboard service. It runs your agent in a containerized environment and once a scenario run is complete transitions to the next.
