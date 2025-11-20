
![Logo](docs/image.png)


# Incalmo: An Autonomous LLM-Based Multi-Stage Attacker

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
![GitHub issues](https://img.shields.io/github/issues/bsinger98/Incalmo?style=flat-square)
![GitHub pull requests](https://img.shields.io/github/issues-pr/bsinger98/Incalmo?style=flat-square)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/bsinger98/Incalmo?style=flat-square)
![GitHub contributors](https://img.shields.io/github/contributors/bsinger98/Incalmo?style=flat-square)
![GitHub stars](https://img.shields.io/github/stars/bsinger98/Incalmo?style=flat-square)
![GitHub forks](https://img.shields.io/github/forks/bsinger98/Incalmo?style=flat-square)

**Research Paper**: [On the Feasibility of Using LLMs to Execute Multistage Network Attacks](https://arxiv.org/abs/2501.16466)

**Incalmo** is an autonomous AI-driven network penetration testing tool that automatically conducts intelligent red-teaming activities with the aim to enhance and assist operator abilities when performing complex network attack tasks.

---


## Table Of Contents
## Demo

Insert gif or link to demo


## Prerequisites

- **[Docker Desktop](https://www.docker.com/)**
- **[Node.js](https://nodejs.org/en)** (Optional: only needed for [UI Interface](#ui-interface-optional))

## Installation

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
   cd incalmo/frontend/incalmo-ui
   npm install
   ```

#### 3. Start the React Server

Once dependencies are installed, run the react server:

   ```bash
   npm start
   ```

This will lauch the frontend at [http://localhost:3000](http://localhost:3000)

    
## Usage/Examples

```

```


## Tech Stack

**Server:** Node, Express


## Project Structure

```
Incalmo/
├── .dockerignore              # Docker build exclusions
├── .env                       # Environment variables (API keys, debug settings)
├── .env.example               # Template for environment configuration
├── .gitignore                 # Git exclusions (venv, cache, db files)
├── CITATION.cff               # Research paper citation metadata
├── LICENSE                    # MIT License
├── main.py                    # CLI entry point - runs Incalmo strategy
├── pyproject.toml             # Project dependencies and metadata (uv/pip)
├── uv.lock                    # Dependency lock file for reproducibility
├── README.md                  # Project Guide
├── config/                    # Configuration management
│   ├── attacker_config.py     # AttackerConfig model 
│   ├── config.json            # Active configuration file 
│   └── config_example.json    # LLM strategy configuration template
├── docker/                    # Docker containerization
│   ├── docker-compose.yml     # Multi-container orchestration (attacker, webserver, db)
│   ├── docker-compose.attacker.yml  # Standalone attacker service
│   │
│   ├── attacker/              # Attacker container configuration
│   │   ├── incalmo.Dockerfile # Incalmo Dockerfile
│   │   └── start.sh           # Container startup script
│   │
│   └── equifax/               # Target environment (Equifax breach simulation)
│       ├── database/          # Database server container
│       │   ├── Dockerfile     # SSH server with stored credentials
│       │   ├── data.json      # Sensitive data payload
│       │   ├── authorized_keys
│       │   └── id_rsa.pub
│       │
│       └── webserver/         # Web server container
│           ├── Dockerfile     # Apache Struts vulnerable application
│           ├── ssh/           # SSH configuration
│           │   ├── config
│           │   ├── id_rsa
│           │   └── id_rsa.pub
│           └── struts/        # Vulnerable Struts application files
├── incalmo/                   # Core application code
│   ├── exceptions.py          # Custom exceptions 
│   ├── incalmo_runner.py      # Main strategy execution runner
│   ├── server.py              # Flask server entry point
│   │
│   ├── api/                   # Client API for C2 server communication
│   │   └── server_api.py      # C2ApiClient 
│   │
│   ├── c2server/              # Command & Control server
│   │   ├── c2server.py        # Main Flask application
│   │   ├── shared.py          # Shared utilities, state management, and constants
│   │   ├── state_store.py     # SQLite-based environment state persistence
│   │   │
│   │   ├── agents/            # Agent implementations
│   │   │   └── sandcat.go     # Go-based agent
│   │   │
│   │   ├── celery/            # Async task queue
│   │   │   ├── celery_app.py  # Celery application factory
│   │   │   ├── celery_tasks.py    # Task definitions 
│   │   │   └── celery_worker.py   # Worker configuration 
│   │   │
│   │   ├── payloads/          # Exploit and deployment payloads
│   │   │   ├── sandcat.go         # Agent source code
│   │   │   ├── sandcat.go-linux   # Compiled Linux agent
│   │   │   ├── createBindShellCronJob.sh
│   │   │   ├── downloadAgent.sh
│   │   │   ├── runDeployAgent.sh
│   │   │   ├── runHackerAgent.sh
│   │   │   ├── strutsExploit.py   
│   │   │   ├── sudo_baron_exploit.py
│   │   │   ├── sudo_bypass.py
│   │   │   ├── sudoedit_exploit.sh
│   │   │   ├── writeable_passwd.sh
│   │   │   ├── writeable_sudoers_exploit.sh
│   │   │   └── template_payloads/
│   │   │       └── Exec_Bash_Template.sh
│   │   │
│   │   └── routes/            # Flask blueprints for API endpoints
│   │       ├── agent_routes.py        # Agent management
│   │       ├── command_routes.py      # Command execution and status polling
│   │       ├── environment_routes.py  # Environment state updates
│   │       ├── file_routes.py         # File upload/download operations
│   │       ├── llm_routes.py          # LLM action queue management
│   │       ├── logging_routes.py      # Log retrieval and streaming
│   │       └── strategy_routes.py     # Strategy lifecycle
│   │
│   ├── core/                  # Core attack framework
│   │   ├── actions/           # Action classes 
│   │   │   ├── high_level_action.py   # Abstract base for high-level actions
│   │   │   ├── low_level_action.py    # Abstract base for low-level commands
│   │   │   │
│   │   │   ├── EmptyServiceActions/   # Placeholder actions
│   │   │   │   ├── escelate_privledge.py
│   │   │   │   ├── exfiltrate_data.py
│   │   │   │   ├── find_information_on_host.py
│   │   │   │   ├── lateral_move.py
│   │   │   │   └── scan.py
│   │   │   │
│   │   │   ├── HighLevel/         # High-level actions
│   │   │   │   ├── scan.py                    # Network/host reconnaissance
│   │   │   │   ├── lateral_move_to_host.py    # Single-host lateral movement
│   │   │   │   ├── attack_path_lateral_move.py # Multi-hop lateral movement
│   │   │   │   ├── escelate_privledge.py      # Privilege escalation orchestration
│   │   │   │   ├── find_information_on_host.py # File/credential discovery
│   │   │   │   ├── exfiltrate_data.py         # Data exfiltration
│   │   │   │   │
│   │   │   │   └── llm_agents/        # LLM-agent action implementations
│   │   │   │       ├── llm_agent_action.py    # Base LLM agent action class
│   │   │   │       ├── scan/                  # LLM scanning 
│   │   │   │       ├── lateral_movement/      # LLM lateral move 
│   │   │   │       ├── privilege_escalation/  # LLM privesc 
│   │   │   │       ├── find_information/      # LLM information gathering
│   │   │   │       └── exfiltrate_data/       # LLM data exfiltration
│   │   │   │
│   │   │   └── LowLevel/          # Low-level commands
│   │   │       ├── run_bash_command.py        # Generic bash execution
│   │   │       ├── scan_network.py            # Network discovery 
│   │   │       ├── scan_host.py               # Host service enumeration
│   │   │       ├── nikto_scan.py              # Web vulnerability scanning
│   │   │       ├── ssh_lateral_move.py        # SSH-based lateral movement
│   │   │       ├── nc_lateral_move.py         # Netcat reverse shell
│   │   │       ├── scp_file.py                # Secure file copy
│   │   │       ├── exploit_struts.py          # Struts exploitation
│   │   │       ├── find_ssh_config.py         # SSH credential discovery
│   │   │       ├── add_ssh_key.py             # SSH key persistence
│   │   │       ├── read_file.py               # Remote file reading
│   │   │       ├── write_file.py              # Remote file writing
│   │   │       ├── copy_file.py               # Local file copy
│   │   │       ├── list_files_in_directory.py # File list
│   │   │       ├── md5sum_attacker_data.py    # MD5Sum Information
│   │   │       ├── wgetFile.py                # File download
│   │   │       └── privledge_escalation/      # Privilege escalation exploits
│   │   │           ├── check_passwd_permissions.py
│   │   │           ├── get_sudo_version.py
│   │   │           ├── sudo_baron.py
│   │   │           ├── sudoedit_exploit.py
│   │   │           ├── writeable_passwd.py
│   │   │           └── writeable_sudoers_exploit.py
│   │   │
│   │   ├── models/            # Core domain models
│   │   │   ├── events/        # Event system for state updates
│   │   │   │   ├── __init__.py
│   │   │   │   ├── event.py                   # Base event class
│   │   │   │   ├── bash_output_event.py
│   │   │   │   ├── hosts_discovered_event.py
│   │   │   │   ├── services_discovered_on_host_event.py
│   │   │   │   ├── vulnerable_service_found_event.py
│   │   │   │   ├── scan_report_event.py
│   │   │   │   ├── infected_new_host_event.py
│   │   │   │   ├── root_access_on_host_event.py
│   │   │   │   ├── credentail_found_event.py
│   │   │   │   ├── files_found_event.py
│   │   │   │   ├── file_contents_found_event.py
│   │   │   │   ├── critical_data_found_event.py
│   │   │   │   ├── exfiltrated_data_event.py
│   │   │   │   ├── flag_found_event.py
│   │   │   │   ├── sudo_version_event.py
│   │   │   │   └── writeable_sudoers_event.py
│   │   │   │
│   │   │   └── network/       # Network infrastructure models
│   │   │       ├── network.py             # Network topology container
│   │   │       ├── subnet.py              # Subnet representation
│   │   │       ├── host.py                # Host with services and vulnerabilities
│   │   │       ├── open_port.py           # Port and service info
│   │   │       ├── credential.py          # Authentication credentials
│   │   │       ├── scan_results.py        # Scan result aggregation
│   │   │       └── attack_path.py         # Attack graph path representation
│   │   │
│   │   ├── services/          # Core logic services
│   │   │   ├── __init__.py
│   │   │   ├── config_service.py              # Configuration loading and management
│   │   │   ├── environment_initializer.py     # Environment setup and bootstrap
│   │   │   ├── environment_state_service.py   # State tracking and event processing
│   │   │   ├── attack_graph_service.py        # Attack path planning and graph analysis
│   │   │   ├── action_context.py              # Context management for action execution
│   │   │   ├── high_level_action_orchestrator.py  # High-level action coordination
│   │   │   ├── low_level_action_orchestrator.py   # Low-level command execution
│   │   │   └── logging_service.py             # Structured logging
│   │   │
│   │   └── strategies/        # Attack strategies
│   │       ├── incalmo_strategy.py    # Abstract base strategy class
│   │       ├── strategy_factory.py    # Strategy instantiation factory
│   │       ├── strategy_registry.py   # Dynamic strategy discovery and registration
│   │       │
│   │       ├── llm/               # LLM-based strategies
│   │       │   ├── llm_strategy.py            # Base LLM strategy
│   │       │   ├── langchain_strategy.py      # LangChain-based strategy implementation
│   │       │   ├── langchain_registry.py      # LangChain tool registration
│   │       │   ├── llm_agent_registry.py      # LLM agent registration
│   │       │   ├── llm_response.py            # LLM response parsing and validation
│   │       │   │
│   │       │   └── interfaces/        # LLM interfaces and prompts
│   │       │       ├── llm_interface.py
│   │       │       ├── langchain_interface.py
│   │       │       ├── llm_agent_interface.py
│   │       │       └── preprompts/    # System prompts and templates
│   │       │
│   │       ├── state_machine/     # Rule-based strategies
│   │       │   ├── __init__.py
│   │       │   ├── graph_search.py        # Base graph search strategy
│   │       │   ├── bfs.py                 # Breadth-first search strategy
│   │       │   ├── dfs.py                 # Depth-first search strategy
│   │       │   ├── struts_strategy.py     # Apache Struts exploitation chain
│   │       │   ├── equifax_test.py        # Equifax breach simulation
│   │       │   ├── MHBench_equifax_test.py # MHBench evaluation harness
│   │       │   ├── darkside.py            # DarkSide ransomware simulation
│   │       │   └── debug.py               # Debug/testing strategy
│   │       │
│   │       ├── testers/           # Strategy testing utilities
│   │       │
│   │       └── util/              # Strategy utilities
│   │           └── event_util.py  # Event processing helpers
│   │
│   ├── frontend/              # Web interface
│   │   └── incalmo-ui/        # React-based UI
│   │       ├── .gitignore
│   │       ├── package.json       # Node.js dependencies
│   │       ├── tsconfig.json      # TypeScript configuration
│   │       ├── README.md
│   │       ├── public/            # Static assets
│   │       └── src/               # React components and application logic
│   │
│   └── models/                # Shared data models (Pydantic)
│       ├── __init__.py
│       ├── agent.py               # Agent representation 
│       ├── command.py             # Command structure with status enum
│       ├── command_result.py      # Command execution results
│       ├── instruction.py         # Agent instruction format
│       ├── llm_agent_action_data.py   # LLM action data transfer object
│       └── logging_schema.py      # Structured logging schemas
└── output/                    # Execution logs and results

```
## License

This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License