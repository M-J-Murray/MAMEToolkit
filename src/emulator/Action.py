class Action(object):

    def __init__(self, port, field):
        self.port = port
        self.field = field

    def get_lua_string(self):
        return 'iop.ports["' + self.port + '"].fields["' + self.field + '"]'
