import json
from aiohttp import web
import os

from app.service.auth_svc import for_all_public_methods, check_authorization


@for_all_public_methods(check_authorization)
class DeceptionAPI:

    def __init__(self, services):
        self.services = services
        self.auth_svc = self.services.get("auth_svc")
        self.data_svc = self.services.get("data_svc")

    async def mirror(self, request):
        """
        This sample endpoint mirrors the request body in its response
        """
        request_body = json.loads(await request.read())
        return web.json_response(request_body)

    async def get_logs(self, request):
        """
        This endpoint returns the last log entry from the logs table
        """
        # Get experiment name from request
        experiment = request.match_info.get("experiment", None)
        if experiment is None:
            return web.json_response({"error": "Experiment name not provided"})

        log_data = {}
        logs_dir = "logs/" + experiment

        llm_log_path = os.path.join(logs_dir, "llm.log")
        perry_log_path = os.path.join(logs_dir, "perry.log")
        low_level_action_log_path = os.path.join(logs_dir, "low_level_action.json")
        high_level_action_log_path = os.path.join(logs_dir, "high_level_action.json")
        preprompt_log_path = os.path.join(logs_dir, "pre_prompt.log")
        bash_log_path = os.path.join(logs_dir, "bash_log.log")

        # Check if llm log exists
        if os.path.exists(llm_log_path):
            with open(llm_log_path, "r") as llm_log:
                # Read entire file
                log_data["llm"] = llm_log.read()
        else:
            log_data["llm"] = None

        # Check if perry log exists
        if os.path.exists(perry_log_path):
            with open(perry_log_path, "r") as perry_log:
                log_data["perry"] = perry_log.read()
        else:
            log_data["perry"] = None

        if os.path.exists(low_level_action_log_path):
            with open(low_level_action_log_path, "r") as low_level_action_log:
                log_data["low_level_action"] = low_level_action_log.read()
        else:
            log_data["low_level_action"] = None

        if os.path.exists(high_level_action_log_path):
            with open(high_level_action_log_path, "r") as high_level_action_log:
                log_data["high_level_action"] = high_level_action_log.read()
        else:
            log_data["high_level_action"] = None

        # Check if preprompt log exists
        if os.path.exists(preprompt_log_path):
            with open(preprompt_log_path, "r") as preprompt_log:
                log_data["preprompt"] = preprompt_log.read()
        else:
            log_data["preprompt"] = None

        # Check if bash log exists
        if os.path.exists(bash_log_path):
            with open(bash_log_path, "r") as bash_log:
                log_data["bash"] = bash_log.read()
        else:
            log_data["bash"] = None

        # convert to json and return
        return web.json_response(log_data)

    async def post_initial_parameters(self, request):
        """
        This endpoint receives the initial parameters for the deception plugin
        """
        data = await request.json()
        data = json.loads(data)

        # Save parameters
        data_dir = "plugins/deception/app/data/config.json"
        with open(data_dir, "w") as f:
            json.dump(data, f)

        return web.json_response({"status": "success"})
