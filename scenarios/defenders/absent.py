from scenarios.Scenario import DefenderInformation

absent = DefenderInformation(
    name="Absent",
    telemetry="NoTelemetry",
    strategy="StaticStandalone",
    capabilities={
        "DeployDecoy": 0,
        "HoneyService": 0,
        "RestoreServer": 0,
        "HoneyCredentials": 0,
    },
)
