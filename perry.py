import click
import openstack
import json
from datetime import datetime
import os

from ansible.AnsibleRunner import AnsibleRunner
from config.Config import Config
from cli.attacker import attacker
from cli.environment import env
from cli.experiment import experiment
from cli.benchmark import bench
from cli.dev import dev
from cli.cli_context import PerryContext
from cli.llm_maker import llm


@click.group()
@click.pass_context
def main(ctx):
    # Load the configuration
    with open("config/config.json", "r") as file:
        config = Config(**json.load(file))

    # Add to context
    perry_util = PerryContext(config=config)
    ctx.obj = perry_util


main.add_command(attacker)
main.add_command(env)
main.add_command(experiment)
main.add_command(bench)
main.add_command(dev)
main.add_command(llm)


if __name__ == "__main__":
    main()
