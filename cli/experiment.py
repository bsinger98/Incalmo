import click
import importlib
from os import path
import json

from cli.cli_context import PerryContext
from scenarios.Scenario import Experiment
from emulator.experiment_runner import ExperimentRunner

attacker_module = importlib.import_module("attacker")


def load_instance(config_path: str):
    """Dynamically import the instance from the given config path."""
    try:
        module = importlib.import_module(config_path)
        return getattr(module, "experiment")
    except (ImportError, AttributeError) as e:
        raise click.BadParameter(f"Failed to load instance from '{config_path}': {e}")


@click.command()
@click.option("--type", help="The experiment module to use", required=True, type=str)
@click.option(
    "--compile-first-environment",
    help="Compile the first environment",
    is_flag=True,
    default=False,
)
@click.pass_context
def experiment(ctx, type: str, compile_first_environment: bool):
    context: PerryContext = ctx.obj

    config_path = f"scenarios.experiments.{type}"
    experiment = load_instance(config_path)
    if not isinstance(experiment, list) and not all(
        isinstance(exp, Experiment) for exp in experiment
    ):
        raise click.BadParameter(
            f"Failed to load instance from '{type}': not an Experiment instance"
        )

    experiment_runner = ExperimentRunner(experiment, context.config)
    experiment_runner.run(compile_first_environment=compile_first_environment)
