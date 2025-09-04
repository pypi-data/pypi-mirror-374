import unittest

import rt_client.v2.client
import requests_mock


class V2ClientTestCase(unittest.TestCase):
    @requests_mock.Mocker()
    def test_create_client_and_authenticate_with_password(self, request_mocker):
        request_mocker.post("https://rt.host.com/NoAuth/Login.html")
        rt_client.v2.client.Client("username", "password", "https://rt.host.com/")
        self.assertEqual("POST", request_mocker.request_history[0].method)
        self.assertEqual(
            "https://rt.host.com/NoAuth/Login.html",
            request_mocker.request_history[0].url,
        )
        # Confirm that the username and password where used for auth
        self.assertEqual(
            "user=username&pass=password", request_mocker.request_history[0].text
        )

    @requests_mock.Mocker()
    def test_request_retries_if_the_session_has_expired(self, request_mocker):
        request_mocker.post("https://rt.host.com/NoAuth/Login.html")
        expected_json = {"id": 123456}
        # return 401 to indicate that the session cookie has expired,
        # second request returns the ticket json
        request_mocker.get(
            "https://rt.host.com/tickets/123456",
            [{"status_code": 401}, {"status_code": 200, "json": expected_json}],
        )
        client = rt_client.v2.client.Client(
            "username", "password", "https://rt.host.com/"
        )
        request_mocker.reset()
        ticket_json = client.request("GET", "https://rt.host.com/tickets/123456")
        self.assertEqual(ticket_json, expected_json)
        self.assertEqual(3, request_mocker.call_count)
        self.assertEqual(
            "https://rt.host.com/tickets/123456", request_mocker.request_history[0].url
        )
        self.assertEqual(
            request_mocker.request_history[1].url,
            "https://rt.host.com/NoAuth/Login.html",
        )
        self.assertEqual(
            request_mocker.request_history[2].url, "https://rt.host.com/tickets/123456"
        )


if __name__ == "__main__":
    unittest.main()
