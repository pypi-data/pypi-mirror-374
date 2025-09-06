# © 2025 SAP SE or an SAP affiliate company. All rights reserved.

from typing import Any
from bdc_connect_sdk.models.certificate_information import CertificateInformation

class PartnerClient:
    def get_access_token(self, cert_info: CertificateInformation, share_name: str) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def get_bdc_connect_endpoint(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def get_bdc_connect_tenant(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def build_create_or_update_share_request_body(self, body: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Subclasses should implement this method.")

# © 2025 SAP SE or an SAP affiliate company. All rights reserved.
