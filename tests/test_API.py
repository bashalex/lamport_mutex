from threading import Thread
from time import time, sleep
from unittest import TestCase
from mutex import LamportMutex
from utils.logger import Logger


class MockConnection:
    """
    unittest.mock.MagicMock can be used instead of this class
    """
    # constants
    __REQUEST = 0
    __RELEASE = 1
    __CONFIRM = 2

    CORRECT_NUM_OF_CONFIRMATIONS = 0
    NO_CONFIRMATIONS = 1
    WRONG_NUM_OF_CONFIRMATIONS = 2

    state = CORRECT_NUM_OF_CONFIRMATIONS

    def __init__(self, id, port, other_ids, other_ports, cb):
        self.id = id
        self.port = port
        self.cb = cb
        self.other_ids = other_ids

    def send(self, recipient_id, message, time):
        # used only for confirmations
        # do not await answer here
        pass

    def broadcast(self, message, time):
        if message != self.__REQUEST:
            # do not await any responses
            return
        if self.state == self.CORRECT_NUM_OF_CONFIRMATIONS:
            # await len(self.other_ids) number of confirmations
            for _id in self.other_ids:
                self.cb((self.__CONFIRM, _id, 0))  # last argument is logic time. don't care about it here
        elif self.state == self.WRONG_NUM_OF_CONFIRMATIONS:
            if len(self.other_ids) > 1:
                self.cb((self.__CONFIRM, self.other_ids[0], 0))
        elif self.state == self.NO_CONFIRMATIONS:
            pass

    def simulate_request_from_other_process(self, other_time):
        self.cb((self.__REQUEST, self.other_ids[0], other_time))

    def simulate_release_from_other_process(self, other_time, after):
        sleep(after)
        self.cb((self.__RELEASE, self.other_ids[0], other_time))

    def tear_down(self):
        pass


class TestAPI(TestCase):
    """
    Don't really care about logger error messages during tests
    """

    def setUp(self):
        self.mutex_path = '../mutex.txt'
        self.logger = Logger(debug=False)
        self.logger.warn('Ignore logger error during tests!')
        self.other_ids = [i for i in range(1, 10)]
        self.other_ports = [8100 + i for i in range(1, 10)]

        self.mutex = LamportMutex(self.mutex_path, 0, 8000,
                                  self.other_ids, self.other_ports, self.logger)
        self.mutex.tear_down()  # kill real connection

        # mock connection
        self.mock_connection = MockConnection(0, 8000, self.other_ids,
                                              self.other_ports, self.mutex.api.on_response)
        self.mutex.api.connection = self.mock_connection

    def test__API_with_correct_answers(self):
        """
        mock connection works correctly
        """
        self.mock_connection.state = MockConnection.CORRECT_NUM_OF_CONFIRMATIONS

        # mutex must be acquired
        self.assertEqual(self.mutex.lock(), True)  # acquire mutex
        self.mutex.unlock()  # release mutex

    def test__API_with_wrong_answer(self):
        """
        mock connection send less confirmation than required
        """
        self.mock_connection.state = MockConnection.WRONG_NUM_OF_CONFIRMATIONS

        # timeout supposed to be here
        self.assertEqual(self.mutex.lock(), False)  # acquire mutex

    def test__API_without_answer(self):
        """
        actually is the same that previous one
        """
        self.mock_connection.state = MockConnection.NO_CONFIRMATIONS

        # timeout supposed to be here
        self.assertEqual(self.mutex.lock(), False)  # acquire mutex

    def test__API_increment_clock(self):
        """
        test whether clock increment works correctly
        """
        self.mock_connection.state = MockConnection.CORRECT_NUM_OF_CONFIRMATIONS

        # simulate request
        other_time = 10
        self.mock_connection.simulate_request_from_other_process(other_time)  # time bigger than ours
        # add 1 after receiving
        # add one more 1 after sending confirmation
        self.assertEqual(self.mutex.api.clock, other_time + 2)

        # now out time is equal to other_time + 2
        # let's receive 'release' message with older time than ours now:
        self.mock_connection.simulate_release_from_other_process(other_time + 1, 0)
        # our time is supposed to be equal to other_time + 3 now:
        # because we only increment it once when receive 'release' message
        self.assertEqual(self.mutex.api.clock, other_time + 3)

    def test__API_other_locks_earlier(self):
        """
        check that we await until mutex is released before lock it
        """
        # mock connection
        self. mock_connection.state = MockConnection.CORRECT_NUM_OF_CONFIRMATIONS

        # simulate request
        self.mock_connection.simulate_request_from_other_process(-1)  # earlier than our time

        # simulate release after 1.5s
        delay = 1.5
        thread = Thread(target=self.mock_connection.simulate_release_from_other_process, args=(1, delay))
        thread.start()

        start = time()
        self.mutex.lock()

        # locked only after ~1.5s => OK
        self.assertGreaterEqual(time(), start + delay)

        self.mutex.unlock()

    def test__API_other_locks_later(self):
        """
        lock mutex if our process is first in the queue
        """
        self.mock_connection.state = MockConnection.CORRECT_NUM_OF_CONFIRMATIONS

        # simulate release after 1.5s
        delay = 1.5
        thread = Thread(target=self.mock_connection.simulate_release_from_other_process, args=(1, delay))
        thread.start()

        start = time()
        self.mutex.lock()

        # simulate request
        self.mock_connection.simulate_request_from_other_process(10)  # later than our time

        # locked before delay passed=> OK
        self.assertLess(time(), start + delay)

        self.mutex.unlock()
