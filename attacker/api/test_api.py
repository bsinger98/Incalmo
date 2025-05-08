from api.server_api import C2ApiClient, Results
from incalmo.actions.low_level_action import LowLevelAction
from incalmo.models.events import Event


class WhoamiAction(LowLevelAction):
    async def get_result(self, results: Results) -> list[Event]:
        print("STDOUT:", results.stdout)
        print("STDERR:", results.stderr)
        return []


print("Get agents")
client = C2ApiClient()
prior_agents = client.get_agents()
print("Agents:")
for agent in prior_agents:
    print(agent.paw)
action = WhoamiAction(agent=prior_agents[0], command="whoami")
command_result = client.send_command(action)
print(command_result.__str__())
