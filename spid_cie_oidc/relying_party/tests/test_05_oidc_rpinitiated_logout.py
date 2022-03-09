from django.contrib.auth import get_user_model, login
from django.test import Client, TestCase
from django.urls import reverse


class RpIntiatedLogoutTest(TestCase):

    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="superuser", password="secret", email="admin@example.com"
        )

        
    def test_rpinitaited_logout(self):
        c = Client()
        c.login(username="superuser", password="secret")
        url = reverse("spid_cie_rpinitiated_logout")
        res = c.get(url)
        self.assertTrue(res.status_code == 302)
