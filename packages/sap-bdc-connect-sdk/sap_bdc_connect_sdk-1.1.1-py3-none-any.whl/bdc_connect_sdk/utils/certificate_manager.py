# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
import datetime
import hashlib
import base64
from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class CertificateManager:
    def get_certificate_base64_hash(self, cert_pem: bytes):
        cert = load_pem_x509_certificate(cert_pem, default_backend())
        certificate_der = cert.public_bytes(encoding=serialization.Encoding.DER)

        hash_sha256 = hashlib.sha256(certificate_der).digest()
        return base64.urlsafe_b64encode(hash_sha256).decode('utf-8').rstrip('=')
    
    def generate_self_signed_certificate(self):
        one_day = datetime.timedelta(1, 0, 0) # 1 day
        expiration_days = datetime.timedelta(15, 0, 0) # 15 days
        
        private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend())
        public_key = private_key.public_key()

        builder = x509.CertificateBuilder()
        builder = builder.subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "bdc-python-sdk")]))
        builder = builder.issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "bdc-python-sdk")]))
        builder = builder.not_valid_before(datetime.datetime.today() - one_day)
        builder = builder.not_valid_after(datetime.datetime.today() + expiration_days)
        builder = builder.serial_number(x509.random_serial_number())
        builder = builder.public_key(public_key)
        builder = builder.add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        
        certificate = builder.sign(
            private_key=private_key,
            algorithm=hashes.SHA256(),
            backend=default_backend()
        )

        cert = certificate.public_bytes(serialization.Encoding.PEM)
        key = private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        )

        return (cert, key)

# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
