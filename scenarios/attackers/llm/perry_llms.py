from attacker.config.attacker_config import AbstractionLevel
from scenarios.Scenario import AttackerInformation

### Google LLMs ###
gemini1_5_pro_perry = AttackerInformation(
    name="Gemini1.5Pro_perry",
    strategy="gemini_15_pro_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)
gemini1_5_flash_perry = AttackerInformation(
    name="Gemini1.5Flash_perry",
    strategy="gemini_15_flash_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)
gemini2_flash_perry = AttackerInformation(
    name="Gemini2Flash_perry",
    strategy="gemini_2_flash_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)
gemini2_5_pro_perry = AttackerInformation(
    name="Gemini2_5Pro_perry",
    strategy="gemini_2_5_pro_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)


### OpenAI LLMs ###
gpt4o_mini_perry = AttackerInformation(
    name="GPT4oMini_perry",
    strategy="gpt4o_mini_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)

gpt4o_perry = AttackerInformation(
    name="GPT4o_perry",
    strategy="gpt4o_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)

gpto1_perry = AttackerInformation(
    name="GPTo1_perry",
    strategy="gpto1_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)

### Anthropic LLMs ###
haiku3_5_perry = AttackerInformation(
    name="Haiku3_5_perry",
    strategy="haiku3_5_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)

sonnet3_perry = AttackerInformation(
    name="Sonnet3_perry",
    strategy="sonnet3_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)

sonnet3_5_perry = AttackerInformation(
    name="Sonnet3.5_perry",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)
sonnet3_7_thinking_perry = AttackerInformation(
    name="Sonnet3_7_thinking_perry",
    strategy="sonnet3_7_thinking_strategy",
    abstraction=AbstractionLevel.HIGH_LEVEL,
)
