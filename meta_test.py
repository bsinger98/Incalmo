import json

from incalmo.core.services.metasploit_service import MetasploitService

metaservice = MetasploitService("password")
result = metaservice.connect_to_session_via_bind("192.168.200.20")
print(
    json.dumps(
        result[0].model_dump(),
        indent=2,
    )
)
print(
    json.dumps(
        result[1].model_dump(),
        indent=2,
    )
)
result = metaservice.list_sessions()
print(json.dumps([m.model_dump() for m in result], indent=2))
