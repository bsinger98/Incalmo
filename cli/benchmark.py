import click
import importlib
import time

from environment.environment import Environment

env_module = importlib.import_module("environment")


@click.group()
@click.option("--env", help="The environment", required=True, type=str)
@click.pass_context
def bench(ctx, env: str):
    # Deploy deployment instance
    deployment_instance_ = getattr(env_module, env)
    environment: Environment = deployment_instance_(
        ctx.obj.ansible_runner,
        ctx.obj.openstack_conn,
        ctx.obj.config.external_ip,
        ctx.obj.config,
    )
    # Add deployment instance to context
    ctx.obj.environment = environment


@bench.command()
@click.pass_context
def setup(ctx):
    click.echo("Setting up the environment...")

    # Time setup for 5 trials
    trials = 5
    times = []
    for _ in range(trials):
        start_time = time.time()
        ctx.obj.environment.setup()
        ctx.obj.environment.runtime_setup()
        end_time = time.time()

        trial_time = end_time - start_time
        times.append(trial_time)
        click.echo(f"Trial time: {trial_time}")

    average_time = sum(times) / trials
    click.echo(f"Average time: {average_time}")
    click.echo(times)


@bench.command()
@click.option("--trials", help="Number of trials", required=True, type=int)
@click.pass_context
def compile(ctx, trials: int):
    click.echo("Compiling the environment (can take several hours)...")

    # Time compilation for 5 trials
    times = []

    for _ in range(trials):
        try:
            start_time = time.time()
            ctx.obj.environment.compile(True, True)
            end_time = time.time()

            trial_time = end_time - start_time
            times.append(trial_time)
            click.echo(f"Trial time: {trial_time}")
        except Exception as e:
            click.echo(f"Error: {e}")

    average_time = sum(times) / trials
    click.echo(f"Average time: {average_time}")
    click.echo(times)
