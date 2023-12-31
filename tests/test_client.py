from client import Marzban
from unittest import TestCase


class TestClient(TestCase):
    def setUp(self):
        self.client = Marzban(base_url="http://panel.chobekhob.xyz:8000/")
        print(self.client.get_admin_token("salam", "salam"))
        # with Marzban(base_url="http://panel.chobekhob.xyz:8000/") as s:
        #     pass
        
    def test_client(self):
        pass
