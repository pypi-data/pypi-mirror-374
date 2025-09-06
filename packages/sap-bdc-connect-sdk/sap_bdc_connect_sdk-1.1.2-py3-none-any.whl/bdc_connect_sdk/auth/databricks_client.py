# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
import json
import re
from typing import Any, TypeVar, cast
import jwt
import requests
import urllib

from bdc_connect_sdk.auth.partner_client import PartnerClient
from bdc_connect_sdk.models.certificate_information import CertificateInformation
from bdc_connect_sdk.utils import warnings

T = TypeVar("T")
RESPONSE_TEXT_MAX_LENGTH = 200

class DatabricksClient(PartnerClient):
    def __init__(self, dbutils: Any, recipient_name: str | None = None) -> None:
        self.dbutils: Any = dbutils
        notebook_context = dbutils.notebook.entry_point.getDbutils().notebook().getContext() #type: ignore
        self.databricks_workspace_url: str = str(notebook_context.apiUrl().getOrElse(None)) #type: ignore
        self.databricks_api_token: str = str(notebook_context.apiToken().getOrElse(None)) #type: ignore

        self.recipient_name: str | None = recipient_name
        self.is_brownfield_environment: bool = _is_brownfield_environment(self.recipient_name, self.databricks_workspace_url, self.databricks_api_token)
        self.bdc_connect_endpoint: str = ""
        self.bdc_connect_tenant: str = ""
        self.bdc_connect_access_token_information: dict[str, str] = {
            "share_url": "",
            "client_id": "",
            "share_location": ""
        }
        
    def get_access_token(self, cert_info: CertificateInformation, share_name: str) -> str:
        if self.is_brownfield_environment:
            return self._get_access_token_for_bdc_connect(cert_info, share_name)
        
        return self._get_access_token_for_databricks_connect(cert_info, share_name)
    
    def get_bdc_connect_endpoint(self) -> str:
        if not self.bdc_connect_endpoint:
            if self.is_brownfield_environment:
                self.bdc_connect_endpoint = _extract_bdc_connect_endpoint(self.bdc_connect_access_token_information["share_location"])
            else:
                self.bdc_connect_endpoint = self._get_secret("api_url")

        return self.bdc_connect_endpoint
    
    def get_bdc_connect_tenant(self) -> str:
        if not self.bdc_connect_tenant:
            if self.is_brownfield_environment:
                self.bdc_connect_tenant = self._extract_tenant_from_bdc_connect_endpoint()
            else:
                self.bdc_connect_tenant = self._get_secret("tenant")
        
        return self.bdc_connect_tenant
    
    def build_create_or_update_share_request_body(self, body: dict[str, Any]) -> dict[str, Any]:
        if "type" not in body:
            body["type"] = "REMOTE_SHARE"
        else:
            if body["type"] != "REMOTE_SHARE":
                raise ValueError("The 'type' field must be 'REMOTE_SHARE' for Databricks shares.")
            
            warnings.warn_user(
                "The 'type' field is now set automatically. "
                "Providing it manually is no longer necessary."
            )

        if "provider" not in body:
            body["provider"] = {
                "type": "FEDERATION"
            }
        else:
            if body["provider"].get("type") != "FEDERATION":
                raise ValueError("The 'provider.type' field must be 'FEDERATION' for Databricks shares.")
            
            warnings.warn_user(
                "The 'provider' field is now set automatically. "
                "Providing it manually is no longer necessary."
            )

        if self.is_brownfield_environment:
            body["provider"]["name"] = self.bdc_connect_access_token_information["client_id"]
            body["provider"]["url"] = self.bdc_connect_access_token_information["share_url"]
        else:
            body["provider"]["name"] = "databricks"

        return body
        
    def _get_access_token_for_bdc_connect(self, cert_info: CertificateInformation, share_name: str) -> str:
        endpoint = '/api/2.0/partnerhub/delta-sharing/retrieve-partner-token'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.databricks_api_token}'
        }

        payload = {
            'cnf_x5t_sha256': cert_info.cert_base64_hash,
            'share_name': share_name,
            'recipient_name': str(self.recipient_name)
        }
        
        response = requests.post(
            url=f'{self.databricks_workspace_url}{endpoint}',
            json=payload,
            headers=headers
        )

        try:
            data = response.json()
        except ValueError as e:
            content_preview = response.text[:RESPONSE_TEXT_MAX_LENGTH] if hasattr(response, "text") else str(response)
            raise ValueError(f"Response is not valid JSON. Status code: {response.status_code}, Content: {content_preview}") from e

        if "access_token" not in data:
            raise ValueError(f"Error when trying to obtain 'access_token' from JSON response: {data}")
        
        access_token = data.get("access_token")

        self._store_access_token_information(access_token)

        return access_token
    
    def _get_access_token_for_databricks_connect(self, cert_info: CertificateInformation, share_name: str) -> str:
        bdc_connect_endpoint = self.get_bdc_connect_endpoint()
        tenant = self.get_bdc_connect_tenant()
        id_token = self._get_id_token(cert_info.cert_base64_hash)
        return _get_databricks_connect_access_token(tenant, bdc_connect_endpoint, share_name, id_token, cert_info.cert_temp_file_name, cert_info.key_temp_file_name)
    
    def _get_secret(self, secret: str) -> str:
        return self.dbutils.secrets.get("sap-bdc-connect-sdk", secret) #type: ignore
    
    def _extract_tenant_from_bdc_connect_endpoint(self) -> str:
        match = re.search(r'https://([^\.]+)', self.get_bdc_connect_endpoint())

        if match:
            return match.group(1)
        
        return ""
    
    def _get_id_token(self, cert_base64_hash: str) -> str:
        endpoint = '/oidc/v1/token'
        audience = self._get_secret("token_audience")
        
        payload = {
            'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
            'subject_token': self.databricks_api_token,
            'subject_token_type': 'urn:databricks:params:oauth:token-type:personal-access-token',
            'requested_token_type': 'urn:ietf:params:oauth:token-type:id_token',
            'scope': 'openid profile email',
            'audience': audience,
            'cnf_x5t_sha256': cert_base64_hash
        }

        response = requests.post(self.databricks_workspace_url + endpoint, data=payload)

        try:
            data = response.json()
        except ValueError as e:
            content_preview = response.text[:RESPONSE_TEXT_MAX_LENGTH] if hasattr(response, "text") else str(response)
            raise ValueError(f"Response is not valid JSON. Status code: {response.status_code}, Content: {content_preview}") from e

        if "id_token" not in data:
            raise ValueError(f"'id_token' not found in JSON response: {data}")
        
        return data.get("id_token")
    
    def _store_access_token_information(self, access_token: str) -> None:
        try:
            jwt_payload: dict[str, Any] = jwt.decode(access_token, options={"verify_signature": False})
            
            authorization_details: list[dict[str, Any]] = _get_required_field(jwt_payload, "authorization_details", "authorization_details")
            _validate_list(authorization_details, "authorization_details")

            self.bdc_connect_access_token_information["client_id"] = _get_required_field(jwt_payload, "client_id", "client_id")
            self.bdc_connect_access_token_information["share_location"] = _get_share_location_from_authorization_details(authorization_details)
            self.bdc_connect_access_token_information["share_url"] = _get_share_url_from_authorization_details(authorization_details)
            
        except Exception as e:
            raise RuntimeError(f"Failed to extract information from BDC Connect access_token: {e}")

def _is_brownfield_environment(recipient_name: str | None, databricks_workspace_url: str, databricks_api_token: str) -> bool:
    if not recipient_name:
        return False
    
    endpoint = f'/api/2.1/unity-catalog/recipients/{recipient_name}'

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {databricks_api_token}'
    }

    response = requests.get(
        url=f'{databricks_workspace_url}{endpoint}',
        headers=headers
    )

    try:
        data = response.json()
    except ValueError as e:
        content_preview = response.text[:RESPONSE_TEXT_MAX_LENGTH] if hasattr(response, "text") else str(response)
        raise ValueError(f"Response is not valid JSON. Status code: {response.status_code}, Content: {content_preview}") from e

    if "error_code" in data and "message" in data:
        raise ValueError(f"{data.get('error_code')}: {data.get('message')}")

    if "properties_kvpairs" not in data or "properties" not in data.get('properties_kvpairs', {}):
        raise ValueError(data)

    return data.get('properties_kvpairs', {}).get('properties', {}).get('databricks.partnerConnectionId') is not None

def _extract_bdc_connect_endpoint(bdc_connect_share_endpoint: str) -> str:
    match = re.search(r'(https://[^/]+/)', bdc_connect_share_endpoint)
    if match:
        return match.group(1)
    return ""

def _get_databricks_connect_access_token(tenant: str, url_base: str, share_name: str, id_token: str, cert_temp_file_name: str, key_temp_file_name: str) -> str:
    endpoint = '/oauth2/token'

    headers = {
        'X-SAP-FileContainer': tenant,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    authorization_details: list[dict[str, Any]] = [{
        'resources': [{
                'name': f'catalog:share:{share_name}',
                'type': 'REMOTE_SHARE',
                'provider': {
                    'type': 'FEDERATION',
                    'name': 'databricks'
                }
        }],
        'privileges': [
            'create',
            'append',
            'delete'
        ]
    }]

    payload = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
        'subject_token': id_token,
        'subject_token_type': 'urn:ietf:params:oauth:token-type:id_token',
        'requested_token_type': 'urn:ietf:params:oauth:token-type:access_token',
        'authorization_details': json.dumps(authorization_details)
    }

    encoded_payload = str(urllib.parse.urlencode(payload)) #type: ignore

    response = requests.post(
        url_base + endpoint,
        headers=headers,
        data=encoded_payload,
        cert=(cert_temp_file_name, key_temp_file_name),
        verify=True
    )

    try:
        data = response.json()
    except ValueError as e:
        content_preview = response.text[:RESPONSE_TEXT_MAX_LENGTH] if hasattr(response, "text") else str(response)
        raise ValueError(f"Response is not valid JSON. Status code: {response.status_code}, Content: {content_preview}") from e

    if "access_token" not in data:
        raise ValueError(f"Response format is not as expected: {data}")
    
    return data.get("access_token")

def _get_share_location_from_authorization_details(authorization_details: list[dict[str, Any]]) -> str:
        locations: list[str] = _get_required_field(authorization_details[0], "locations", "authorization_details.locations")
        _validate_list(locations, "authorization_details.locations")
        return locations[0]
    
def _get_share_url_from_authorization_details(authorization_details: list[dict[str, Any]]) -> str:
        additional_properties: list[dict[str, Any]] = _get_required_field(authorization_details[0], "additional_properties", "authorization_details.additional_properties")
        _validate_list(additional_properties, "authorization_details.additional_properties")

        url: str = _get_required_field(additional_properties[0], "url", "authorization_details.additional_properties.url")
        return url

def _get_required_field(payload: dict[str, Any], key: str, key_description: str) -> T: #type: ignore
    value = payload.get(key)
    
    if value is None:
        raise KeyError(f"'{key_description}' claim not found in token")
    
    return cast(T, value)

def _validate_list(list: list[Any], list_name: str) -> None:
    if not list:
        raise KeyError(f"'{list_name}' claim is empty in token")


# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
