from client import Marzban
from models import Admin
from unittest import TestCase


class TestClient(TestCase):
    @classmethod
    def setUpClass(self):
        self.client = Marzban(base_url="http://0.0.0.0:8000/")
        print(self.client.get_admin_token(Admin(
            username="admin",
            password="12345"
        )))
        
        print("_-_-_-_-_-_-_-_-_-_-_ SETUP DONE _-_-_-_-_-_-_-_-_-_-_")
        
    def test_get_current_admin(self):
        print(self.client.get_current_admin())
        
    def test_create_admin(self):
        print(
            self.client.create_admin(
                Admin(
                    username="test",
                    is_sudo=False,
                    password="test"
                )
            )
        )
        
    #TODO: test_set_admin
    #TODO: test_modify_admin
    #TODO: test_delete_admin
    #TODO: test_get_admins
    #TODO: test_get_admins_generator
    #TODO: test_get_admin
        
