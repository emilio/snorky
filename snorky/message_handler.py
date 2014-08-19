from snorky.log import snorky_log
from snorky.hashable import make_hashable
import json


class MessageHandler(object):
    def __init__(self, services=None):
        self.registered_services = {}
        if services:
            for service in services:
                self.register_service(service)

    def register_service(self, service):
        self.registered_services[service.name] = service

    def unregister_service(self, service):
        del self.registered_services[service.name]

    def process_message_from(self, client, msg):
        try:
            service_name = msg["service"]
            content = msg["message"]
        except KeyError:
            snorky_log.warning("Malformed message from client %s: %s"
                           % (client.remote_address, msg))
            return

        try:
            service = self.registered_services[service_name]
        except KeyError:
            snorky_log.warning(
                'Message for non existing service "%s" from client %s'
                % (service_name, client.remote_address))
            return

        service.process_message_from(client, content)

    def process_message_raw(self, client, msg):
        try:
            decoded_msg = make_hashable(json.loads(msg))
        except ValueError:
            snorky_log.warning('Invalid JSON from client %s: %s'
                            % (client.remote_address, msg))
            return

        return self.process_message_from(client, decoded_msg)

    def client_connected(self, client):
        for service in self.registered_services.values():
            service.client_connected(client)

    def client_disconnected(self, client):
        for service in self.registered_services.values():
            service.client_disconnected(client)
