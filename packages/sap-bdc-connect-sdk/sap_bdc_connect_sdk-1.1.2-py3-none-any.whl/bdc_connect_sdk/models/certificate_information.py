# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
import tempfile

from bdc_connect_sdk.utils.certificate_manager import CertificateManager

class CertificateInformation:
    def __init__(self, cert_pem: bytes, key_pem: bytes) -> None:
        self.cert_pem = cert_pem
        self.key_pem = key_pem
        self.cert_base64_hash = CertificateManager().get_certificate_base64_hash(cert_pem)
        self.cert_temp_file_name = _generate_temp_file_name(cert_pem)
        self.key_temp_file_name = _generate_temp_file_name(key_pem)

def _generate_temp_file_name(file_content: bytes) -> str:
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file_content)
    temp_file.flush()
    return temp_file.name

# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
