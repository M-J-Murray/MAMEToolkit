from test.emulator.pipes.AddressTest import AddressTest
from test.emulator.pipes.PipeTest import PipeTest
from test.emulator.pipes.DataPipeTest import DataPipeTest
from test.emulator.StreamGobblerTest import StreamGobblerTest
from test.emulator.ConsoleTest import ConsoleTest
from test.emulator.EmulatorTest import EmulatorTest
import unittest
import os
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_emulator_suite():
    suite = unittest.TestSuite()
    suite.addTest(AddressTest('luaStringTest'))
    suite.addTest(AddressTest('invalidLuaStringTest'))

    suite.addTest(PipeTest('writeTest'))
    suite.addTest(PipeTest('readTest'))
    suite.addTest(PipeTest('readlnEmptyTest'))
    suite.addTest(PipeTest('readFromWritePipeTest'))
    suite.addTest(PipeTest('writeToReadPipeTest'))
    suite.addTest(PipeTest('luaStringTest'))

    suite.addTest(DataPipeTest('luaStringTest'))
    suite.addTest(DataPipeTest('readDataTest'))

    suite.addTest(StreamGobblerTest('readLinesTest'))

    suite.addTest(ConsoleTest('writeReadTest'))

    suite.addTest(EmulatorTest('screenDimensionsTest'))
    suite.addTest(EmulatorTest('stepTest'))

    return suite


if __name__ == "__main__":
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(get_emulator_suite())
