import logging
from aiohttp_jinja2 import template

from app.service.auth_svc import for_all_public_methods, check_authorization
from app.utility.base_world import BaseWorld
from plugins.deception.app.deception_svc import DeceptionService


@for_all_public_methods(check_authorization)
class DeceptionGUI(BaseWorld):

    def __init__(self, services, name, description):
        self.name = name
        self.description = description
        self.services = services
        self.deception_svc = DeceptionService(services)

        self.auth_svc = services.get('auth_svc')
        self.log = logging.getLogger('deception_gui')

    @template('deception.html')
    async def splash(self, request):
        return dict(name=self.name, description=self.description)

    # Add functions here that the front-end will use

