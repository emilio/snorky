import random
import functools
from miau.common.types import MultiDict

__all__ = ('UnknownSubscription', 'SubscriptionManager')

safe_random = random.SystemRandom()


class UnknownSubscription(Exception):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return "No subscription with token '%s'." % self.token


class SubscriptionManager(object):
    """Tracks subscriptions"""

    def __init__(self):
        self.subscriptions_by_token = {}
        self.subscriptions_by_client = MultiDict()

    @staticmethod
    def generate_token():
        return "".join([
            safe_random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
            for i in range(32)
        ])

    def register_subscription(self, subscription):
        """
        Registers a Subscription in the SubscriptionManager, assigning a secret
        unique token to it.

        It is needed for a Subscription to be authorized before a client can
        acquire it.

        Returns the new token.
        """

        if subscription.token:
            raise RuntimeError("This subscription already has a token.")

        while True:
            token = self.generate_token()

            # It's almost impossible that the same token is generated twice,
            # but it's better to be safe than sorry.
            if not token in self.subscriptions_by_token:
                break

        subscription.token = token
        self.subscriptions_by_token[token] = subscription

        return token

    def unregister_subscription(self, subscription):
        """
        Unregisters the Subscription object and removes its token.

        Note: Calling this method does not dettach the subscription items from
        the dealer. To fully delete a subscription from the system see
        `DataSyncService.cancel_subscription`.
        """

        token = subscription.token
        del self.subscriptions_by_token[token]

        subscription.token = None

    def get_subscription_with_token(self, token):
        """Returns a Subscription with the specified token."""

        try:
            return self.subscriptions_by_token[token]
        except KeyError:
            raise UnknownSubscription(token)

    def link_subscription_to_client(self, subscription, client):
        subscription.got_client(client)

        self.subscriptions_by_client.add(client, subscription)

    def unlink_subscription_from_client(self, subscription):
        client = subscription.client
        subscription.lost_client()

        self.subscriptions_by_client.remove(client, subscription)