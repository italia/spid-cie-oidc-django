from django.test import Client, TestCase
from django.urls import reverse


class CallBackEchoAttributesTest(TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_call_back_echo_attributes(self):
        client = Client()
        url = reverse("spid_cie_rp_echo_attributes")
        session = client.session
        session.update({"oidc_rp_user_attrs": {"email":"test@test.it"}})
        session.save()
        res = client.get(url)
        self.assertTrue(res.status_code == 200)
        self.assertTrue("test@test.it" in res.content.decode())
