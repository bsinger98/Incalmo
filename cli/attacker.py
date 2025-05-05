import click

from cli.cli_context import PerryContext
from attacker.Attacker import Attacker
from attacker.config.attacker_config import AttackerConfig, AbstractionLevel, LLM


@click.group()
@click.pass_context
@click.option("--strategy", help="The attacker strategy", required=True, type=str)
@click.option("--env", help="The attacker environment", required=True, type=str)
@click.option(
    "--abstraction", help="The level of Perry's abstraction", required=False, type=str
)
@click.option(
    "--llm",
    help="The LLM you want to use to run the experiment: sonnet3_5, haiku3_5, gpt4omini, gpt4o, gemini1_5",
    required=False,
    type=str,
)
def attacker(ctx, strategy: str, env: str, abstraction: str | None, llm: str | None):
    context: PerryContext = ctx.obj

    if abstraction is None:
        abstraction = AbstractionLevel.HIGH_LEVEL
    else:
        abstraction = AbstractionLevel(abstraction)

    if llm is None:
        llm = LLM.SONNET3_5
    else:
        llm = LLM(llm)

    # Check if env is valid
    # Setup attacker module
    c2c_server = f"http://{context.config.external_ip}:8888"
    attacker_config = AttackerConfig(
        name=f"{strategy}: {env}",
        strategy=strategy,
        environment=env,
        abstraction=abstraction,
        llm=llm,
        c2c_server=c2c_server
    )

    context.attacker = Attacker(
        context.config.caldera_config.api_key,
        attacker_config,
        context.experiment_id,
    )


@attacker.command()
@click.pass_context
def start(ctx):
    context: PerryContext = ctx.obj
    if context.attacker is None:
        raise Exception("Attacker not initialized")

    click.echo("Starting attacker")
    context.attacker.start_operation()
