import click
from defender.llm_maker.llm_maker import LLMMaker


@click.command()
@click.option(
    "--perry-sdk/--no-perry-sdk",
    default=True,
    help="Use Perry SDK for LLM conversation.",
)
def llm(perry_sdk):
    llm_maker = LLMMaker(perry_sdk=perry_sdk)
    llm_maker.send_message("Please create a deception strategy")
    llm_maker.save_conversation("deception_convo.txt")
