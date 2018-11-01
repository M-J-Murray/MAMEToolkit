# A class used to help abstract and simplify the process of setting up a memory address that you want to read from
class Address(object):

    def __init__(self, address, mode):
        self.address = address
        self.mode = mode

    def get_lua_string(self):
        try:
            return {
                'u8': 'mem:read_u8('+self.address+')',
                'u16': 'mem:read_u16('+self.address+')',
                'u32': 'mem:read_u32('+self.address+')',
                's8': 'mem:read_i8('+self.address+')',
                's16': 'mem:read_i16('+self.address+')',
                's32': 'mem:read_i32('+self.address+')'
            }[self.mode]
        except KeyError:
            raise IOError("Invalid address mode used")
