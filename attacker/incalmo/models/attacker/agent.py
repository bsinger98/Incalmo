import marshmallow as ma

class AgentFieldsSchema(ma.Schema):

    paw = ma.fields.String(allow_none=True)
    sleep_min = ma.fields.Integer()
    sleep_max = ma.fields.Integer()
    watchdog = ma.fields.Integer()
    group = ma.fields.String()
    architecture = ma.fields.String()
    platform = ma.fields.String()
    server = ma.fields.String()
    upstream_dest = ma.fields.String(allow_none=True)
    username = ma.fields.String()
    location = ma.fields.String()
    pid = ma.fields.Integer()
    ppid = ma.fields.Integer()
    trusted = ma.fields.Boolean()
    executors = ma.fields.List(ma.fields.String())
    privilege = ma.fields.String()
    exe_name = ma.fields.String()
    host = ma.fields.String()
    contact = ma.fields.String()
    proxy_receivers = ma.fields.Dict(keys=ma.fields.String(), values=ma.fields.List(ma.fields.String()),
                                     allow_none=True)
    proxy_chain = ma.fields.List(ma.fields.List(ma.fields.String()), allow_none=True)
    origin_link_id = ma.fields.String()
    deadman_enabled = ma.fields.Boolean(allow_none=True)
    available_contacts = ma.fields.List(ma.fields.String(), allow_none=True)
    host_ip_addrs = ma.fields.List(ma.fields.String(), allow_none=True)

    display_name = ma.fields.String(dump_only=True)
    created = ma.fields.DateTime()
    last_seen = ma.fields.DateTime()
    pending_contact = ma.fields.String()

    @ma.pre_load
    def remove_nulls(self, in_data, **_):
        return {k: v for k, v in in_data.items() if v is not None}

    @ma.pre_load
    def remove_properties(self, data, **_):
        data.pop('display_name', None)
        data.pop('created', None)
        data.pop('last_seen', None)
        data.pop('links', None)
        return data


class AgentSchema(AgentFieldsSchema):

    @ma.post_load
    def build_agent(self, data, **kwargs):
        return None if kwargs.get('partial') is True else Agent(**data)