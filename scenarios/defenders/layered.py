from scenarios.Scenario import DefenderInformation

layered_d10_h10 = DefenderInformation(
    name="Layered_d10_h10",
    telemetry="NoTelemetry",
    strategy="StaticLayered",
    capabilities={
        "DeployDecoy": 10,
        "HoneyService": 0,
        "RestoreServer": 0,
        "HoneyCredentials": 10,
    },
)
