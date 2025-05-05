from attacker.config.attacker_config import AbstractionLevel
from scenarios.Scenario import AttackerInformation

### Google LLMs ###
gemini1_5_pro_low_level = AttackerInformation(
    name="Gemini1.5Pro_low_level",
    strategy="gemini_15_pro_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)
gemini1_5_flash_low_level = AttackerInformation(
    name="Gemini1.5Flash_low_level",
    strategy="gemini_15_flash_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)
gemini2_flash_low_level = AttackerInformation(
    name="Gemini2Flash_low_level",
    strategy="gemini_2_flash_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)
gemini2_5_pro_low_level = AttackerInformation(
    name="Gemini2_5Pro_low_level",
    strategy="gemini_2_5_pro_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)

### OpenAI LLMs ###
gpt4o_mini_low_level = AttackerInformation(
    name="GPT4oMini_low_level",
    strategy="gpt4o_mini_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)

gpt4o_low_level = AttackerInformation(
    name="GPT4o_low_level",
    strategy="gpt4o_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)

### Anthropic LLMs ###
haiku3_5_low_level = AttackerInformation(
    name="Haiku3_5_low_level",
    strategy="haiku3_5_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)

sonnet3_low_level = AttackerInformation(
    name="Sonnet3_low_level",
    strategy="sonnet3_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)

sonnet3_5_low_level = AttackerInformation(
    name="Sonnet3.5_low_level",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.LOW_LEVEL,
)
