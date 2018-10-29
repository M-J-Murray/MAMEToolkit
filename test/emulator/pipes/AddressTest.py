import unittest
from hamcrest import *
from src.emulator.pipes.Address import Address


class AddressTest(unittest.TestCase):

    def test_lua_string(self):
        assert_that(Address('test','u8').get_lua_string(), equal_to('manager:machine().devices[":maincpu"].spaces["program"]:read_u8(test)'))
        assert_that(Address('test','u16').get_lua_string(), equal_to('manager:machine().devices[":maincpu"].spaces["program"]:read_u16(test)'))
        assert_that(Address('test','u32').get_lua_string(), equal_to('manager:machine().devices[":maincpu"].spaces["program"]:read_u32(test)'))
        assert_that(Address('test','s8').get_lua_string(), equal_to('manager:machine().devices[":maincpu"].spaces["program"]:read_i8(test)'))
        assert_that(Address('test','s16').get_lua_string(), equal_to('manager:machine().devices[":maincpu"].spaces["program"]:read_i16(test)'))
        assert_that(Address('test','s32').get_lua_string(), equal_to('manager:machine().devices[":maincpu"].spaces["program"]:read_i32(test)'))

    def test_invalid_lua_string(self):
        with self.assertRaises(Exception) as context:
            Address('test','INVALID').get_lua_string(),
        assert_that(str(context.exception), contains_string('Invalid address mode used'))