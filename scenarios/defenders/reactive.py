from scenarios.Scenario import DefenderInformation

reactive_layered_d10_h10 = DefenderInformation(
    name="ReactiveLayered_d10_h10",
    telemetry="SimpleTelemetryAnalysis",
    strategy="ReactiveLayered",
    capabilities={
        "DeployDecoy": 10,
        "HoneyService": 0,
        "RestoreServer": -1,
        "HoneyCredentials": 10,
    },
)
