# Incalmo: An Autonomous LLM-Based Multi-Stage Attacker

📄 **Research Paper**: [On the Feasibility of Using LLMs to Execute Multistage Network Attacks](https://arxiv.org/abs/2501.16466)

## Quick Start Guide

### Prerequisites

- **[Docker Desktop](https://www.docker.com/)**

### Setup Instructions

#### 1. Configure the Application

Create your configuration file by copying the example:

```bash
cp config/config_example.json config/config.json
```

Then edit `config/config.json` to match your setup requirements.

#### 2. Set Up API Keys

Create your environment file by copying the example:

```bash
cp .env.example .env
```

Then edit `.env` and add your LLM API keys.



#### 3. Start the Development Environment

Navigate to the docker directory and start the containers:

```bash
cd docker
docker compose up
```


#### 4. Run Incalmo

In a new terminal window, attach to the running container and execute Incalmo:

   ```bash
   cd docker
   docker compose exec attacker /bin/bash
   uv run incalmo.py
   ```