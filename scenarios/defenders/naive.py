from scenarios.Scenario import DefenderInformation

naive = DefenderInformation(
    name="Naive",
    telemetry="NoTelemetry",
    strategy="StaticStandalone",
    capabilities={
        "DeployDecoy": 3,
        "HoneyService": 3,
        "RestoreServer": 3,
        "HoneyCredentials": 3,
    },
)
