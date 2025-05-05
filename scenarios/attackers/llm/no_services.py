from attacker.config.attacker_config import AbstractionLevel
from scenarios.Scenario import AttackerInformation

### Google LLMs ###
gemini1_5_pro_no_services = AttackerInformation(
    name="Gemini1.5Pro_no_services",
    strategy="gemini_15_pro_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)
gemini1_5_flash_no_services = AttackerInformation(
    name="Gemini1.5Flash_no_services",
    strategy="gemini_15_flash_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)
gemini2_flash_no_services = AttackerInformation(
    name="Gemini2Flash_no_services",
    strategy="gemini_2_flash_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)
gemini2_5_no_services = AttackerInformation(
    name="Gemini2_5Pro_no_services",
    strategy="gemini_2_5_pro_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)

### OpenAI LLMs ###
gpt4o_mini_no_services = AttackerInformation(
    name="GPT4oMini_no_services",
    strategy="gpt4o_mini_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)

gpt4o_no_services = AttackerInformation(
    name="GPT4o_no_services",
    strategy="gpt4o_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)

### Anthropic LLMs ###
haiku3_5_no_services = AttackerInformation(
    name="Haiku3_5_no_services",
    strategy="haiku3_5_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)

sonnet3_no_services = AttackerInformation(
    name="Sonnet3_no_services",
    strategy="sonnet3_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)

sonnet3_5_no_services = AttackerInformation(
    name="Sonnet3.5_no_services",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.NO_SERVICES,
)
