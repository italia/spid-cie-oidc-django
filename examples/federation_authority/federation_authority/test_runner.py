from django.test.runner import DiscoverRunner


class SpidCieOidcDiscoverRunner(DiscoverRunner):
    def build_suite(self, test_labels=None, **kwargs):
        if not test_labels:
            test_labels = ["spid_cie_oidc"]
        return super().build_suite(test_labels, **kwargs)
