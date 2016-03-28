# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.test import Client
import json
from unittest import TestCase
import unittest


class TestListSubscribe(TestCase):
    def setUp(self):
        self.client = Client()

    def test_thing(self):
        response = self.client.get("/api/tasks/", HTTP_X_SNORKY="Subscribe")
        self.assertEqual(response.status_code, 200)

        self.assertTrue(response["Content-Type"].startswith(
            "application/json"))
        self.assertTrue(response.has_header("X-Subscription-Token"))

        data = json.loads(response.content.decode("UTF-8"))


if __name__ == "__main__":
    unittest.main()
