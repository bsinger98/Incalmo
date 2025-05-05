from app.utility.base_world import BaseWorld
from plugins.deception.app.deception_gui import DeceptionGUI
from plugins.deception.app.deception_api import DeceptionAPI

name = "Deception"
description = "Our deception platform"
address = "/plugin/deception/gui"
access = BaseWorld.Access.RED


async def enable(services):
    app = services.get("app_svc").application
    deception_gui = DeceptionGUI(services, name=name, description=description)
    app.router.add_static(
        "/deception", "plugins/deception/static/", append_version=True
    )
    app.router.add_route("GET", "/plugin/deception/gui", deception_gui.splash)

    deception_api = DeceptionAPI(services)
    # Add API routes here
    app.router.add_route("POST", "/plugin/deception/mirror", deception_api.mirror)
    app.router.add_route(
        "GET", "/plugin/deception/get_logs/{experiment}", deception_api.get_logs
    )
    app.router.add_route(
        "POST",
        "/plugin/deception/initial_parameters",
        deception_api.post_initial_parameters,
    )
