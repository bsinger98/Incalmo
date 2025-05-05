import click

from cli.cli_context import PerryContext
from environment.docker_env import DockerEnv
from emulator.docker_emulator import DockerEmulator


@click.group()
@click.pass_context
def dev(ctx):
    context: PerryContext = ctx.obj


@dev.command()
@click.pass_context
def setup(ctx):
    context: PerryContext = ctx.obj

    if context.config.llm_api_keys is None:
        raise Exception("LLM API keys are required for this operation")

    env = DockerEnv("equifax", context.config.llm_api_keys)
    env.setup()


@dev.command()
@click.pass_context
def teardown(ctx):
    context: PerryContext = ctx.obj

    if context.config.llm_api_keys is None:
        raise Exception("LLM API keys are required for this operation")

    env = DockerEnv("equifax", context.config.llm_api_keys)
    env.teardown()


@dev.command()
@click.argument("attack_strategy")
@click.pass_context
def start(ctx, attack_strategy: str):
    context: PerryContext = ctx.obj

    if context.config.llm_api_keys is None:
        raise Exception("LLM API keys are required for this operation")

    env = DockerEnv("equifax", context.config.llm_api_keys)

    emulator = DockerEmulator(context.config, env)
    emulator.start(attack_strategy)
