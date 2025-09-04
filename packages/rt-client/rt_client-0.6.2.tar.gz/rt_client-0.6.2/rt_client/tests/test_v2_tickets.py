import unittest
from unittest import mock
import requests_mock
import tempfile

from rt_client.v2.tickets import TicketManager
from rt_client import exceptions
from rt_client.v2 import client


class V2TicketsTestCase(unittest.TestCase):
    def test_get_all_method_is_not_supported(self):
        manager = TicketManager(mock.MagicMock(name="Client"))
        self.assertRaises(exceptions.UnsupportedOperation, manager.get_all)

    @requests_mock.Mocker()
    def test_stale_session_during_ticket_creation(self, request_mocker):
        request_mocker.register_uri(
            "POST",
            "https://rt.host.com/REST/2.0/ticket",
            [
                {"json": {"message": "Unauthorized"}, "status_code": 401},
                {
                    "json": {
                        "_url": "https://rt.host.com/REST/2.0/ticket/42",
                        "type": "ticket",
                        "id": "42",
                    },
                    "status_code": 200,
                },
            ],
        )
        request_mocker.register_uri(
            "GET",
            "https://rt.host.com/REST/2.0/ticket",
            text="new ticket",
            status_code=200,
        )
        request_mocker.register_uri(
            "POST",
            "https://rt.host.com/NoAuth/Login.html",
            text="Logged in",
            status_code=200,
        )
        rt = client.Client("username", "password", "https://rt.host.com/")
        manager = TicketManager(rt)
        attachment_content = b"This is my attachment\n"
        with tempfile.NamedTemporaryFile(suffix=".txt") as attachment:
            attachment.write(attachment_content)
            attachment.flush()
            details = {
                "Subject": "something is broken",
                "Queue": "support",
                "Content": "Help please",
                "Requestor": "user@cloud.com",
            }
            manager.create(details, [attachment.name])
        self.assertEqual(len(request_mocker.request_history), 4)
        # Initial log in on client creation, first attempt to create ticket,
        # reauthentication, second ticket submission
        expected_paths = [
            "/noauth/login.html",
            "/rest/2.0/ticket",
            "/noauth/login.html",
            "/rest/2.0/ticket",
        ]
        self.assertEqual(
            [h.path for h in request_mocker.request_history], expected_paths
        )
        # Check that the attachment content was included in the re-submission
        self.assertIn(attachment_content, request_mocker.request_history[3].body)
