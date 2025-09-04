import unittest

import requests_mock

from rt_client.v2.attachments import AttachmentManager
import rt_client.v2.client


class AttachmentsTestCase(unittest.TestCase):
    def setUp(self):
        self.attachment_id = "123456"
        self.transaction_id = "100005"
        self.attachment_json = {
            "_hyperlinks": [
                {
                    "id": int(self.attachment_id),
                    "_url": (
                        "https://rt.rest.com/REST/2.0/attachment/" + self.attachment_id
                    ),
                    "type": "attachment",
                    "ref": "self",
                }
            ],
            "MessageId": "",
            "Creator": {
                "_url": "https://rt.host.com/REST/2.0/user/Test.User@email.com",
                "id": "Test.User@email.com",
                "type": "user",
            },
            "ContentType": "image/png",
            "Content": "\x89PNG\r\n" "",
            "id": 545450,
            "Subject": "",
            "Headers": 'Content-Type: image/png; name="image002.png"',
            "Created": "2024-01-14T20:06:57Z",
            "TransactionId": {
                "_url": (
                    "https://rt.host.com/REST/2.0/transaction/" + self.transaction_id
                ),
                "id": self.transaction_id,
                "type": "transaction",
            },
            "Filename": "image002.png",
        }

    def create_client(self, mocker):
        mocker.post("https://rt.host.com/NoAuth/Login.html")
        return rt_client.v2.client.Client(
            username="User", password="**********", endpoint="https://rt.host.com/"
        )

    @requests_mock.Mocker()
    def test_file_url_with_transaction_id(self, requests_mocker):
        attachment = AttachmentManager(self.create_client(requests_mocker))
        requests_mocker.get(
            f"https://rt.host.com/REST/2.0/attachment/{self.attachment_id}",
            json=self.attachment_json,
        )
        file_url = attachment.file_url(
            self.attachment_id, transaction_id=self.transaction_id
        )
        self.assertEqual(
            f"https://rt.host.com/Ticket/Attachment/{self.transaction_id}/{self.attachment_id}",
            file_url,
        )

    @requests_mock.Mocker()
    def test_file_url_without_ticket_id(self, requests_mocker):
        attachment = AttachmentManager(self.create_client(requests_mocker))
        requests_mocker.get(
            f"https://rt.host.com/REST/2.0/attachment/{self.attachment_id}",
            json=self.attachment_json,
        )
        file_url = attachment.file_url(self.attachment_id)
        self.assertEqual(
            f"https://rt.host.com/Ticket/Attachment/{self.transaction_id}/{self.attachment_id}",
            file_url,
        )


if __name__ == "__main__":
    unittest.main()
