# Incalmo: An Autonomous LLM-Based Multi-Stage Attacker

**Research Paper**: [On the Feasibility of Using LLMs to Execute Multistage Network Attacks](https://arxiv.org/abs/2501.16466)

## Quick Start Guide

### Prerequisites

- **[Docker Desktop](https://www.docker.com/)**
- **[Node.js](https://nodejs.org/en)**

### Setup Instructions

#### 1. Setup configuration

Create a configuration file by copying the example:

```bash
cp config/config_example.json config/config.json
```

Then edit `config/config.json` as needed.

#### 2. Set API Keys

Create an environment file by copying the example:

```bash
cp .env.example .env
```

Then add LLM API keys to `.env`.

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
   uv run main.py
   ```

### UI Interface (optional)

If you want to use the web-based interface for Incalmo:

#### 1. Start Backend

Follow Steps 1 through 3 in the [Setup Instructions](#setup-instructions).

#### 2. Install Node.js dependencies

Install Node dependencies:

   ```bash
   cd frontend/incalmo-ui
   npm install
   ```

#### 3. Start the React Server

Once dependencies are installed, run the react server:

   ```bash
   npm start
   ```

This will lauch the frontend at [http://localhost:3000](http://localhost:3000)


