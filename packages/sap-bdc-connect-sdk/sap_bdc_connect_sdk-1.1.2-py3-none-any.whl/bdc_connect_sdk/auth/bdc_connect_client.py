# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
import json
from typing import Any
from bdc_connect_sdk.auth.partner_client import PartnerClient
from bdc_connect_sdk.generated.models.object_info import ObjectInfo
from bdc_connect_sdk.generated.models.put_share_response import PutShareResponse
from bdc_connect_sdk.models.certificate_information import CertificateInformation
from bdc_connect_sdk.utils import warnings
from bdc_connect_sdk.utils.certificate_manager import CertificateManager

from ..generated.api_client import ApiClient, Configuration
from ..generated.api.publish_api import PublishApi

class BdcConnectClient:
    def __init__(self, partner_client: PartnerClient) -> None:
        self.partner_client: PartnerClient = partner_client
        self.cert_info: CertificateInformation | None = None
        self.headers: dict[str, str] | None = None
        self.tenant: str = ""
        self._publish_api_client: PublishApi | None = None

    def __enter__(self) -> "BdcConnectClient":
        warnings.warn_user(
            "Using 'BdcConnectClient' as a context manager is deprecated. "
            "It can be instantiated and used directly without 'with'."
        )
        return self

    def __exit__(self, *_) -> None:
        pass

    def create_or_update_share(self, share_name: str, body: str | dict[str, Any]) -> PutShareResponse | None:
        self._prepare_client_for_request(share_name)

        body = _cast_body_string_to_dict(body)

        body = self.partner_client.build_create_or_update_share_request_body(body)

        if self._publish_api_client:
            return self._publish_api_client.create_or_update_share(share_name, x_sap_file_container=self.tenant, body=json.dumps(body), _headers=self.headers)  

    def create_or_update_share_csn(self, share_name: str, body: str | dict[str, Any]) -> str | None:
        self._prepare_client_for_request(share_name)

        body = _cast_body_string_to_dict(body)

        if self._publish_api_client:
            return self._publish_api_client.create_or_update_share_csn(share_name, x_sap_file_container=self.tenant, body=json.dumps(body), _headers=self.headers)

    def publish_data_product(self, share_name: str) -> str | None:
        self._prepare_client_for_request(share_name)

        if self._publish_api_client:
            return self._publish_api_client.publish_data_product(share_name, x_sap_file_container=self.tenant, _headers=self.headers)

    def delete_share(self, share_name: str, drop_cascade: bool = False) -> ObjectInfo | None:
        self._prepare_client_for_request(share_name)

        if self._publish_api_client:
            return self._publish_api_client.delete_share(share_name, x_sap_file_container=self.tenant, drop_cascade=drop_cascade, _headers=self.headers)

    def _prepare_client_for_request(self, share_name: str) -> None:
        if not self.cert_info:
            cert_pem, key_pem = CertificateManager().generate_self_signed_certificate()
            self.cert_info = CertificateInformation(cert_pem, key_pem)

        access_token = self.partner_client.get_access_token(self.cert_info, share_name)
        bdc_connect_endpoint = self.partner_client.get_bdc_connect_endpoint()
        tenant = self.partner_client.get_bdc_connect_tenant()

        self._initialize_publish_api_client_if_necessary(bdc_connect_endpoint)
        self.tenant = tenant
        self.headers = {
            'X-SAP-Tenant': tenant,
            'Authorization': f'Bearer {access_token}'
        }
    
    def _initialize_publish_api_client_if_necessary(self, bdc_connect_endpoint: str) -> None:
        if not self._publish_api_client:
            config = Configuration()
            config.host = bdc_connect_endpoint

            if self.cert_info:
                config.cert_file = self.cert_info.cert_temp_file_name #type: ignore
                config.key_file = self.cert_info.key_temp_file_name #type: ignore

            self._publish_api_client = PublishApi(ApiClient(configuration=config))

def _cast_body_string_to_dict(body: str | dict[str, Any]):
    body_json: dict[str, Any]

    if isinstance(body, str):
        body_json = json.loads(body)
    else:
        body_json = body

    return body_json
    
# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
