from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
import os
from datetime import datetime

from emulator.emulator import Emulator
from config.Config import Config
from scenarios.Scenario import Experiment

from attacker.exceptions import NoAttackerAgentsError, AttackerServerDownError


class ExperimentRunner:
    def __init__(self, experiments: list[Experiment], config: Config):
        self.experiments = experiments
        self.config = config

    def run(self, compile_first_environment: bool = False):
        # Initialize a rich progress bar
        with Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            TimeElapsedColumn(),
            TimeRemainingColumn(),
        ) as progress:

            # Task to track progress of experiments
            experiment_task = progress.add_task(
                "[cyan]Experiments", total=len(self.experiments)
            )

            last_environment = None
            for experiment in self.experiments:
                compile_environment = False

                # If the first environment is not compiled, compile it
                if compile_first_environment and last_environment is None:
                    compile_environment = True

                # If the environment changes, compile the new environment
                if (
                    last_environment != experiment.scenario.environment
                    and last_environment is not None
                ):
                    compile_environment = True

                self.run_experiment(
                    experiment, progress, compile_environment=compile_environment
                )
                progress.update(experiment_task, advance=1)
                last_environment = experiment.scenario.environment

    def run_experiment(
        self,
        experiment: Experiment,
        progress: Progress,
        compile_environment: bool = False,
    ):
        # Set scenario
        emulator = Emulator(self.config, experiment.scenario)

        if compile_environment:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            directory = f"output/misc/{timestamp}"
            emulator.setup(directory, timestamp, compile=True)
            # Loads all saved snapshots, first load can be glitchy
            emulator.deployment_instance.load_all_snapshots()
            # Restore the topology if any errors occur
            emulator.deployment_instance.deploy_topology()

        experiment_results_dir = f"output/{experiment.scenario}"
        # Check if experiment directory exists
        if not os.path.exists(experiment_results_dir):
            os.makedirs(experiment_results_dir)

        # Task to track progress of trials within the experiment
        trial_task = progress.add_task(
            f"[green]{experiment.scenario} Trials", total=experiment.trials
        )

        for trial in range(experiment.trials):
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            experiment_dir = os.path.join(experiment_results_dir, timestamp)
            try:
                emulator.run_trial(experiment_dir, timestamp, experiment.timeout)
            except NoAttackerAgentsError as error:
                print(error)
                # Rerun the trial
                trial -= 1
            except AttackerServerDownError as error:
                print(error)
                # Rerun the trial
                trial -= 1
            progress.update(trial_task, advance=1)

        progress.remove_task(trial_task)
