# Perry a high-level framework for accelerating security experimentation

🚧🚧🚧 Warning: Documentation is under construction 🚧🚧🚧

## Quick Start Guide

### Prerequisites

- Install Docker
- Install Poetry (Python package manager)
- Install Terraform

### Installation Steps

1. Clone the repository:

   ```bash
   git clone git@github.com:DeceptionProjects/Perry.git --recursive
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Build Docker containers:

   ```bash
   bash build_docker.sh
   ```

4. Create a `config/config.json` (example in `config/config_example.json`)

5. Run an experiment:
   ```bash
   poetry run perry dev start
   ```

## Setup Openstack

Perry requires a local Openstack cloud to run security experiments.

## Setup python environment

1. Install poetry

2. Create environment: `poetry install`

3. Activate environment: `poetry shell`

## Perry CLI

🚧🚧🚧 TODO 🚧🚧🚧

## Start an elasticsearch database

1. Run `docker pull docker.elastic.co/elasticsearch/elasticsearch:8.6.2`

2. Create elastic docker network `docker network create elastic`

3. Start the database `docker run --name elasticsearch --net elastic -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -t docker.elastic.co/elasticsearch/elasticsearch:8.6.2`

For a visual interface you can start Kibana:

1. Pull image `docker pull docker.elastic.co/kibana/kibana:8.6.2`

2. Start image `docker run --name kibana --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.6.2`

**Note**: If you already created the containers (or if they are somehow down), you can start them with `docker start elasticsearch` and `docker start kibana`

## Start a Caldera server

In a new terminal window:

1. Clone the following repo (Brian's fork of Caldera) WITH the `--recursive` flag: https://github.com/bsinger98/caldera

   - `git clone https://github.com/bsinger98/caldera.git --recursive`

2. Add our plugin to Caldera:

   - `cd caldera/plugins`
   - `mkdir deception`
   - `git clone git@github.com:bsinger-cmu/perry-caldera.git deception/`

3. Create another Conda environment for caldera:

   - Create venv
   - `pip install -r caldera/plugins/deception/requirements.txt`

4. Run caldera: `python3 server.py --insecure --fresh`
   - Default ports can be changed by modifying the config file at `conf/default.yml`
   - Check if caldera is running by going to: localhost:8888
   - The credentials for logging in can be found in the configuration file: https://github.com/bsinger98/caldera/blob/master/conf/default.yml
