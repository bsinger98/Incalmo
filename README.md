# Perry: A High-Level Framework for Accelerating Security Experimentation

🚧 **Warning: Documentation is under construction** 🚧

Perry is a high-level Python framework designed to accelerate cybersecurity experimentation, red teaming, and network defense research. It provides an extensible environment for simulating cyber operations, automating agent behaviors, and integrating with tools like Caldera and Dockerized cyber ranges.

## Features

- **Agent-based automation:** Easily script and control agents for offensive or defensive scenarios.
- **Extensible SDK:** Build custom actions, queries, and event handlers.
- **Step-by-step experimentation:** Designed for iterative, explainable security testing.

## Quick Start Guide

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [uv](https://github.com/astral-sh/uv) (Python package/dependency manager)

### Installation Steps

1. **Install dependencies:**

   ```bash
   uv install
   ```

2. **Build Docker containers:**

   ```bash
   cd docker
   docker compose up --build 
   ```

## Usage

Once the containers are running, you can interact with Perry via its Python SDK or through the provided interfaces for agent scripting and scenario execution.

- See the `incalmo/core/strategies/llm/interfaces/preprompts/` directory for example agent prompts and SDK usage.
- For bash-based scenarios, refer to the `bash/pre_prompt.txt` for command-line interaction patterns.

## Documentation

Documentation is under construction. For now, explore the `incalmo/core/` directory and the example prompts for guidance.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.