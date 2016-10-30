import fcntl
from unittest import TestCase, main
from mutex import LamportMutex
from utils.logger import Logger


class MockAPI:
    """
    unittest.mock.MagicMock can be used instead of this class
    """
    clock = 0  # lamport clock
    __number_of_processes = 0  # exclude current

    def __init__(self, ids):
        self.__number_of_processes = len(ids)

    def current_time(self):
        return self.clock

    def request(self, timeout: int) -> int:
        # increment clock and return
        self.clock += 1
        self.clock += self.__number_of_processes  # every confirmation increments clock by 1
        return self.clock

    def confirm(self, recipient_id):
        # increment clock and return
        self.clock += 1

    def release(self):
        # increment clock and return
        self.clock += 1
        return self.clock

    def increment_clock(self):
        # increment clock and return
        self.clock += 1
        return self.clock

    def tear_down(self):
        pass


class TestMutex(TestCase):

    def setUp(self):
        self.mutex_path = '../mutex.txt'
        self.logger = Logger(off=True)
        self.other_ids = [i for i in range(1, 10)]
        self.other_ports = [8100 + i for i in range(1, 10)]

        self.mutex = LamportMutex(self.mutex_path, 0, 8000,
                                  self.other_ids, self.other_ports, self.logger)
        self.mutex.tear_down()  # kill real connection

        # mock API
        mock_api = MockAPI(self.other_ids)
        self.mutex.api = mock_api

    def test__mutex_lock(self):
        # acquire mutex
        self.assertEqual(self.mutex.lock(), True)

        # if mutex was locked resource must be unavailable:
        with open(self.mutex_path, 'w') as f:
            with self.assertRaises(BlockingIOError):
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

        self.mutex.unlock()  # release mutex

    def test__mutex_unlock(self):
        # acquire mutex
        self.assertEqual(self.mutex.lock(), True)
        self.mutex.unlock()  # release mutex

        # resource must be available:
        with open(self.mutex_path, 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
