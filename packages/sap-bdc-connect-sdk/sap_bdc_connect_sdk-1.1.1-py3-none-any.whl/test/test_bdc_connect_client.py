# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
import json
from typing import Any
import unittest
from unittest.mock import patch, MagicMock

from bdc_connect_sdk.auth.bdc_connect_client import BdcConnectClient
from bdc_connect_sdk.auth.databricks_client import DatabricksClient

SHARE_NAME = "dummy_share_name"
CERT_PEM = """
-----BEGIN CERTIFICATE-----
MIIDEDCCAfigAwIBAgIUDc1a7sJsSgyMBm8KNWqmZq4HOrowDQYJKoZIhvcNAQEL
BQAwOTE3MDUGA1UEAwwuaHR0cHM6Ly9kYmMtY2IwM2FjMGUtNTYxZC5jbG91ZC5k
YXRhYnJpY2tzLmNvbTAeFw0yNTAzMTgxNTI3NTZaFw0zMDAzMTgxNTI3NTZaMDkx
NzA1BgNVBAMMLmh0dHBzOi8vZGJjLWNiMDNhYzBlLTU2MWQuY2xvdWQuZGF0YWJy
aWNrcy5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCsLWn0te//
vdkYl61QEWZ+SCmjDQBYi/FxlYkzMjkHmrc5nSf6DdGJkv1ZQr7pOyMGzV9I83Jf
AxohwwUdHYTDBGxB0LQuLCjKlkkkvbLnmWc64mRUuCRuYfixXQoK4DgOVzSkgHYP
5mGqfAnaUrExZytAZS4o4IVETqaAH0U6Pq1QXnEv64AfckQeYcmkIy9Sz2p6zy+M
8yKhYGGgiMK1svQ5aZ/PDpuwt4qWWRtzj0QFepXn30Q7rH/gQlzKVAIzuXTjC+Q/
HK+iFHfX3nt8vOMIgtEBgOBZfqLgpqovofwbRB8cbvQyUUI+IW05m2G4NaoLiAL6
ayw3spaAAwtXAgMBAAGjEDAOMAwGA1UdEwEB/wQCMAAwDQYJKoZIhvcNAQELBQAD
ggEBAH2OBxEvTuLEABVrJz7nc6ntGneDt+ofDNkeoQ5YOOE15QInt1Y0SrDNoM3M
w5CAYy1Op1HiGOQ5JofuS+S63znR+vx25XnbJUAcAmj8UVukx6v6mYvGUAmaPJWW
EyOFwFeGG1sWW1v/WElS/ywrgOXor30maJ9TtD/PjY96tPALjy1SUaF/lTtZtpUC
oXUyQfKxZVHf6dZJ1hmz8aUEHLDT91W7hT84mZ1zhFeiMej6SSEh8+4PK2lCSdcD
lgo2d6k6aJU/+uS2oIFPzNAVoOZgVaTpgo0kg1mNHo5srZ7BwK8WLXI4yYM+NTcH
dvLDABFvT9i9IyGCeo57WcdpWto=
-----END CERTIFICATE-----
"""
ACCESS_TOKEN: str = "dummy_jwt_token"
HOST = "https://cfcselfsigned1.files.hdl.iota-hdl-hc-dev.dev-aws.hanacloud.ondemand.com"
TENANT = "cfcselfsigned1"
HEADERS = {
  'X-SAP-Tenant': TENANT,
  'Authorization': f'Bearer {ACCESS_TOKEN}'
}

class TestBdcConnectClient(unittest.TestCase):
  def setUp(self):
    self.dbx_client = MagicMock()
    self.dbx_client.get_secret.side_effect = lambda secret_name: {"api_url": HOST, "tenant": TENANT}.get(secret_name) #type: ignore
    self.dbx_client.get_access_token.return_value = ACCESS_TOKEN
    self.dbx_client.get_bdc_connect_endpoint.return_value = HOST
    self.dbx_client.get_bdc_connect_tenant.return_value = TENANT
    self.dbx_client.bdc_connect_access_token_information = {
        "client_id": "test_client_id",
        "share_url": "https://test.share.url",
        "share_location": f"{HOST}/shares/{SHARE_NAME}"
    }
    self.dbx_client.recipient_name = None
    self.dbx_client.build_create_or_update_share_request_body.side_effect = lambda body: DatabricksClient.build_create_or_update_share_request_body(self.dbx_client, body) #type: ignore

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.create_or_update_share')
  def test_create_or_update_share(self, mock_create_or_update_share: MagicMock):
    body: dict[str, Any] = {
      "@openResourceDiscoveryV1": {
        "title": SHARE_NAME,
        "shortDescription": f"This is {SHARE_NAME}",
        "description": "This demonstrates that shares can be created and published."
      }
    }

    bdc_connect_client = BdcConnectClient(self.dbx_client)
    bdc_connect_client.create_or_update_share(SHARE_NAME, body)
    self.dbx_client.get_access_token.assert_called_once()
    self.dbx_client.get_bdc_connect_endpoint.assert_called_once()
    self.dbx_client.get_bdc_connect_tenant.assert_called_once()
    mock_create_or_update_share.assert_called_once_with(SHARE_NAME, x_sap_file_container=TENANT, body=json.dumps(body), _headers=HEADERS)

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.create_or_update_share_csn')
  def test_create_or_update_share_csn(self, mock_create_or_update_share_csn: MagicMock):
    body: dict[str, Any] = {
      "definitions": {
        "default": {
          "kind": "context"
        }
      },
      "i18n": {},
      "meta": {
        "creator": "BDS CSN Aggregator 1.0",
        "flavor": "inferred",
        "share_name": SHARE_NAME
      }
    }

    bdc_connect_client = BdcConnectClient(self.dbx_client)
    bdc_connect_client.create_or_update_share_csn(SHARE_NAME, body)
    self.dbx_client.get_access_token.assert_called_once()
    self.dbx_client.get_bdc_connect_endpoint.assert_called_once()
    self.dbx_client.get_bdc_connect_tenant.assert_called_once()
    mock_create_or_update_share_csn.assert_called_once_with(SHARE_NAME, x_sap_file_container=TENANT, body=json.dumps(body), _headers=HEADERS)

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.publish_data_product')
  def test_publish_data_product(self, mock_publish_data_product: MagicMock):
    bdc_connect_client = BdcConnectClient(self.dbx_client)
    bdc_connect_client.publish_data_product(SHARE_NAME)
    self.dbx_client.get_access_token.assert_called_once()
    self.dbx_client.get_bdc_connect_endpoint.assert_called_once()
    self.dbx_client.get_bdc_connect_tenant.assert_called_once()
    mock_publish_data_product.assert_called_once_with(SHARE_NAME, x_sap_file_container=TENANT, _headers=HEADERS)

  @patch('bdc_connect_sdk.auth.bdc_connect_client.PublishApi.delete_share')
  def test_delete_share(self, mock_delete_share: MagicMock):
    bdc_connect_client = BdcConnectClient(self.dbx_client)
    bdc_connect_client.delete_share(SHARE_NAME)
    self.dbx_client.get_access_token.assert_called_once()
    self.dbx_client.get_bdc_connect_endpoint.assert_called_once()
    self.dbx_client.get_bdc_connect_tenant.assert_called_once()
    mock_delete_share.assert_called_once_with(SHARE_NAME, x_sap_file_container=TENANT, drop_cascade=False, _headers=HEADERS)
    

# © 2024-2025 SAP SE or an SAP affiliate company. All rights reserved.
