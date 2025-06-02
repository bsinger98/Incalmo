# Incalmo: An autonomous LLM-based multi-stage attacker

Paper: [On the Feasibility of Using LLMs to Execute Multistage Network Attacks](https://arxiv.org/abs/2501.16466)

## Quick Start Guide

### Prerequisites

- [Docker Desktop](https://www.docker.com/)

### Run

1. Setup configs
- Create `config/config.json` example in `config/config_example.json`
- Add LLM API keys to `.env`, example in `.env.example`

1. Start development environment

   ```bash
   cd docker
   docker compose up
   ```

2. In attacker container, run:

   ```bash
   uv run incalmo.py
   ```