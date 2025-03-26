# ITBench SRE agent

This repository contains the baseline **Site Reliability Engineering (SRE) agent** for [ITBench](https://github.com/IBM/ITBench), a benchmark for evaluating AI agents on real-world IT operations scenarios.

The SRE agent is designed to identify and remediate reliability issues in Kubernetes environments. It connects to observability tools and services deployed by ITBench scenarios and uses LLM reasoning to detect problems, analyze telemetry, and take corrective actions.

---

## ⚙️ Overview

- Connects to deployed [ITBench scenarios](https://github.com/IBM/ITBench-Scenarios)
- Works with monitoring tools like Prometheus, Grafana, and Loki
- Supports multiple LLM backends (via [LiteLLM](https://docs.litellm.ai/docs/providers))
- Built on the [CrewAI](https://github.com/joaomdmoura/crewAI) framework
- Runs fully containerized to prevent unsafe actions on the host machine

---

## 🐳 Running in a container

> Recommended: Always run the agent in a container for safety.

### 1. Clone the repo

```bash
git clone git@github.com:IBM/itbench-sre-agent.git
cd itbench-sre-agent
```

### 2. Create your environment file

```bash
cp .env.tmpl .env
```

Edit `.env` to configure:
- Your LLM provider and model via LiteLLM
- Access details for your Kubernetes cluster and observability tools

### 3. Build the image

```bash
# Docker
docker build -t itbench-sre-agent .

# Podman
podman build -t itbench-sre-agent .
```

### 4. Run the container interactively

```bash
# Docker
docker run -it itbench-sre-agent /bin/bash

# Podman
podman run -it itbench-sre-agent /bin/bash
```

**Linux-only (if bench and agent are on the same host):**

- Port-forward Prometheus:
  ```bash
  kubectl port-forward svc/ingress-nginx-controller -n ingress-nginx 8080:80
  ```
- Run container with `--network=host`:
  ```bash
  docker run --network=host -it itbench-sre-agent /bin/bash
  ```
- Then use `http://localhost:8080/prometheus` as the Grafana URL inside the agent.

### 5. Start the agent

```bash
crewai run
```

> Pre-built images coming soon.

---

## 🧪 Development setup

### 1. Clone the repo

```bash
git clone git@github.com:IBM/itbench-sre-agent.git
cd itbench-sre-agent
```

### 2. Install dependencies

This project uses Python 3.12 and [uv](https://astral.sh/blog/uv/) for fast dependency management.

#### Mac/Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install crewai
```

#### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install crewai
```

### 3. Install dependencies in the project

```bash
crewai install
```

### 4. Set up environment

```bash
cp .env.tmpl .env
```

Update `.env` to configure your LLM and access settings.

### 5. Customize behavior

- `src/lumyn/config/agents.yaml`: Define the agents
- `src/lumyn/config/tasks.yaml`: Define task flows
- `src/lumyn/crew.py`: Add tools, logic, and execution logic
- `src/lumyn/main.py`: Configure agent startup and argument parsing

---

## 🖥️ User interfaces

The agent supports optional UIs for experimentation:

### Panel (Recommended for live debugging)

```bash
cd ui
panel serve panel_main.py --show
```

Open [http://localhost:5006/panel_main](http://localhost:5006/panel_main)

### Streamlit

```bash
cd ui
streamlit run streamlit_main.py
```

Open [http://localhost:5006/panel_main](http://localhost:5006/panel_main)

---

## 🔗 Related links

- [ITBench main repo](https://github.com/IBM/ITBench)
- [ITBench scenarios](https://github.com/IBM/ITBench-Scenarios)
- [ITBench leaderboard](https://github.com/IBM/ITBench-Leaderboard)
- [ITBench CISO agent](https://github.com/IBM/itbench-ciso-caa-agent)
