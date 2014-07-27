import unittest
from mock import Mock
from snorky.server.services.datasync.dealers import Dealer
from snorky.server.services.datasync.delta import \
        Delta, InsertionDelta, UpdateDelta, DeletionDelta


class FakeService(object):
    pass


class FakeSubscription(object):
    def __init__(self):
        self.deliver_delta = Mock()


class FakeSubscriptionItem(object):
    def __init__(self):
        self.subscription = FakeSubscription()


class DummyDealer(Dealer):
    name = 'dummy'

    def __init__(self, test_item):
        super(DummyDealer, self).__init__()
        self.test_item = test_item

    def add_subscription_item(self, item):
        raise NotImplementedError

    def remove_subscription_item(self, item):
        raise NotImplementedError

    def get_subscription_items_for_model(self, model):
        return set([self.test_item])


class TestDealer(unittest.TestCase):
    def setUp(self):
        self.service = FakeService()
        self.test_item = FakeSubscriptionItem()
        # Shorthand
        self.deliver_delta = self.test_item.subscription.deliver_delta

        self.dealer = DummyDealer(self.test_item)

    def test_name(self):
        self.assertEqual(self.dealer.name, 'dummy')

    def test_insertion(self):
        insertion = InsertionDelta('foo', {'id': 1, 'name': 'Alice'})
        self.dealer.deliver_delta(insertion, self.service)

        self.deliver_delta.assert_called_once_with(insertion, self.service)

    def test_update(self):
        update = UpdateDelta('foo',
                {'id': 1, 'name': 'Alice'},
                {'id': 1, 'name': 'Bob'})
        self.dealer.deliver_delta(update, self.service)

        self.deliver_delta.assert_called_once_with(update, self.service)

    def test_deletion(self):
        deletion = DeletionDelta('foo', {'id': 1, 'name': 'Alice'})
        self.dealer.deliver_delta(deletion, self.service)

        self.deliver_delta.assert_called_once_with(deletion, self.service)


if __name__ == "__main__":
    unittest.main()