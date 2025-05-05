from attacker.config.attacker_config import AbstractionLevel
from scenarios.Scenario import AttackerInformation

### Google LLMs ###
gemini1_5_pro_bash = AttackerInformation(
    name="Gemini1.5Pro_bash",
    strategy="gemini_15_pro_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)
gemini1_5_flash_bash = AttackerInformation(
    name="Gemini1.5Flash_bash",
    strategy="gemini_15_flash_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)
gemini2_flash_bash = AttackerInformation(
    name="Gemini2Flash_bash",
    strategy="gemini_2_flash_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

gemini2_5_pro_bash = AttackerInformation(
    name="Gemini2_5Pro_bash",
    strategy="gemini_2_5_pro_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

### OpenAI LLMs ###
gpt4o_mini_bash = AttackerInformation(
    name="GPT4oMini_bash",
    strategy="gpt4o_mini_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

gpt4o_bash = AttackerInformation(
    name="GPT4o_bash",
    strategy="gpt4o_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

gpto1_bash = AttackerInformation(
    name="GPTo1_bash",
    strategy="gpto1_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

### Anthropic LLMs ###
haiku3_5_bash = AttackerInformation(
    name="Haiku3_5_bash",
    strategy="haiku3_5_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

sonnet3_bash = AttackerInformation(
    name="Sonnet3_bash",
    strategy="sonnet3_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

sonnet3_5_bash = AttackerInformation(
    name="Sonnet3.5_bash",
    strategy="sonnet3_5_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)

sonnet3_7_thinking_bash = AttackerInformation(
    name="Sonnet3_7_thinking_bash",
    strategy="sonnet3_7_thinking_strategy",
    abstraction=AbstractionLevel.NO_ABSTRACTION,
)
