import base64

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from django.utils import timezone

from typing import Union

from django.conf import settings


class X509Issuer:

    def __init__(
        self,
        private_key: bytes,
        public_key: bytes,
        subject_data: Union[bytes, None] = None,
        is_ca_or_int: bool = False,
        path_length: int = 0
    ) -> x509.CertificateBuilder:
        """
            returns an X.509 certificate
        """
        # private_key = COSEKey.from_bytes(self.private_key.encode())
        # TODO: add CDP using CRL

        subject_name = [
            x509.NameAttribute(NameOID.COMMON_NAME, subject_data['X509_COMMON_NAME'])
        ] + [
            x509.NameAttribute(NameOID.getattr(i), subject_data[i])
            for i in (
                'COUNTRY_NAME',
                'X509_STATE_OR_PROVINCE_NAME',
                'X509_LOCALITY_NAME',
                'X509_ORGANIZATION_NAME',
            ) if subject_data.get(i)
        ]
        self.cert = (
            x509.CertificateBuilder()
                .issuer_name(
                    x509.Name(
                        [
                            x509.NameAttribute(NameOID.COUNTRY_NAME, settings.X509_COUNTRY_NAME),
                            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, settings.X509_STATE_OR_PROVINCE_NAME),
                            x509.NameAttribute(NameOID.LOCALITY_NAME, settings.X509_LOCALITY_NAME),
                            x509.NameAttribute(NameOID.ORGANIZATION_NAME, settings.X509_ORGANIZATION_NAME),
                            x509.NameAttribute(NameOID.COMMON_NAME, settings.X509_COMMON_NAME)
                        ]
                    )
                )
                .subject_name(x509.Name(subject_name))
                .public_key(public_key)
                .serial_number(x509.random_serial_number())
                .not_valid_before(
                    getattr(settings, "X509_NOT_VALID_BEFORE", None) or
                    subject_data.get('X509_NOT_VALID_BEFORE') or
                    (timezone.localtime() - timezone.timedelta(days=1))
                )
                .not_valid_after(
                    getattr(settings, "X509_NOT_VALID_AFTER", None) or
                    subject_data.get('X509_NOT_VALID_BEFORE') or
                    (timezone.localtime() + timezone.timedelta(days=365))
                )
                .add_extension(
                    x509.BasicConstraints(
                        ca=is_ca_or_int,
                        path_length=path_length
                    ),
                    critical=True,
                )
                .add_extension(
                    x509.SubjectAlternativeName([
                        x509.DNSName(subject_data.get('X509_COMMON_NAME')),
                        x509.UniformResourceIdentifier(subject_data.get('entity_id')),
                    ]),
                    critical=False
                )
                .sign(private_key, hashes.SHA256())
        )

    @property
    def der(self):
        return self.cert.public_bytes(
            getattr(serialization.Encoding, 'DER')
        )

    @property
    def pem(self):
        return self.cert.public_bytes(
            getattr(serialization.Encoding, 'PEM')
        )

    @property
    def x5c(self):
        return [base64.b64encode(self.der).decode('utf-8')]
