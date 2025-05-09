from api.server_api import ApiClient
from incalmo.actions.low_level_action import LowLevelAction
from incalmo.models.events import Event

class WhoamiAction(LowLevelAction):
    async def get_result(self, stdout: str | None, stderr: str | None) -> list[Event]:
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return []

print("Get agents")
client = ApiClient()
prior_agents = client.get_agents()
print("Agents:")
for agent in prior_agents:
    print(agent.paw)
action = WhoamiAction(agent=prior_agents[0], command="whoami")
command_result = client.send_command(action)
print("Command result:", command_result)