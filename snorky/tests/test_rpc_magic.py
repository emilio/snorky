from snorky.server.client import Client
from snorky.server.services.base import RPCService, rpc_command, RPCMeta, \
        asynchronous

from unittest import TestCase
from snorky.tests.utils.rpc import RPCTestMixin


class MockClient(object):
    def __init__(self, test, msg_prop):
        self.test = test
        self.msg_prop = msg_prop

    def send(self, msg):
        setattr(self.test, self.msg_prop, msg)


class CalculatorService(RPCService):
    @rpc_command
    def sum(self, req, a, b):
        return a + b


class CalculatorExtendedService(CalculatorService):
    @rpc_command
    def difference(self, req, a, b):
        return a - b


class ProducerConsumerService(RPCService):
    @asynchronous
    @rpc_command
    def consumer(self, req):
        self.consumer_req = req

    @rpc_command
    def producer(self, req, data):
        self.consumer_req.reply(data)


class TestRPC(RPCTestMixin, TestCase):
    def setUp(self):
        self.client = MockClient(self, "msg")
        self.msg = None
        self.calculator = CalculatorService("calc")
        self.calculator_ex = CalculatorExtendedService("calc_ex")

    def test_rpc_commands(self):
        self.assertEqual(self.calculator.rpc_commands, {"sum"})
        self.assertEqual(self.calculator_ex.rpc_commands,
                         {"sum", "difference"})

    def test_base_existent(self):
        data = self.rpcCall(self.calculator, self.client,
                            "sum", a=5, b=12)
        self.assertEqual(data, 17)

    def test_base_not_existent(self):
        msg = self.rpcExpectError(self.calculator, self.client,
                                  "difference", a=5, b=12)
        self.assertEqual(msg, "Unknown command")

    def test_extended_old_command(self):
        data = self.rpcCall(self.calculator_ex, self.client,
                            "sum", a=5, b=12)
        self.assertEqual(data, 17)

    def test_extended_new_command(self):
        data = self.rpcCall(self.calculator_ex, self.client,
                            "difference", a=5, b=12)
        self.assertEqual(data, -7)

    def test_asynchronous(self):
        client1 = MockClient(self, "client1_msg")
        client2 = MockClient(self, "client2_msg")

        self.client1_msg = None
        self.client2_msg = None

        service = ProducerConsumerService("prodcon")

        # Client 1 calls consumer method
        service.process_message_from(client1, {
            "command": "consumer",
            "callId": 1,
            "params": {}
        })
        # No reply yet
        self.assertEqual(self.client1_msg, None)

        # Client 2 calls producer method
        service.process_message_from(client2, {
            "command": "producer",
            "callId": 2,
            "params": {
                "data": "Hello"
            }
        })
        # Client 2 call returns immediately
        self.assertEqual(self.client2_msg, {
            "service": "prodcon",
            "message": {
                "type": "response",
                "callId": 2,
                "data": None,
            },
        })
        # Client 1 receives its reply now
        self.assertEqual(self.client1_msg, {
            "service": "prodcon",
            "message": {
                "type": "response",
                "callId": 1,
                "data": "Hello"
            }
        })


if __name__ == "__main__":
    unittest.main()