from scenarios.Scenario import DefenderInformation

static_d10 = DefenderInformation(
    name="Layered_d10_h50",
    telemetry="NoTelemetry",
    strategy="StaticLayered",
    capabilities={
        "DeployDecoy": 10,
        "HoneyService": 0,
        "RestoreServer": 0,
        "HoneyCredentials": 0,
    },
)
