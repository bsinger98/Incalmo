from scenarios.Scenario import (
    Scenario,
    Experiment,
    AttackerInformation,
    DefenderInformation,
)


from scenarios.Scenario import (
    Scenario,
    Experiment,
    AttackerInformation,
    DefenderInformation,
)


def generate_experiments(
    attackers: list[AttackerInformation],
    defenders: list[DefenderInformation],
    environments: list[str],
    trials: int = 5,
    skip: list[tuple[AttackerInformation, DefenderInformation, str]] | None = None,
):
    """
    Generate experiments from combinations of attackers, defenders, and environments.

    Args:
        attackers (list): List of attacker configurations
        defenders (list): List of defender configurations
        environments (list): List of environment names
        trials (int): Number of trials for each experiment
        skip (list of tuples, optional): List of (attacker, defender, environment) tuples to skip

    Returns:
        list: List of Experiment objects
    """
    if skip is None:
        skip = []

    experiments = []
    for environment in environments:
        for attacker in attackers:
            for defender in defenders:
                if (attacker, defender, environment) in skip:
                    continue
                experiments.append(
                    Experiment(
                        scenario=Scenario(
                            attacker=attacker,
                            defender=defender,
                            environment=environment,
                        ),
                        trials=trials,
                    )
                )
    return experiments
