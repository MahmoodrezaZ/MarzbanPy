from client import Marzban
from unittest import TestCase


class TestClient(TestCase):
    def setUp(self):
        self.client = Marzban(base_url="http://project.jurchin.xyz:8000/")
        print(self.client.get_admin_token("jurchin", "m22m22m22"))
        
    def test_get_current_admin(self):
        self.client.get_current_admin()
