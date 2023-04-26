import os

from msgraphy.auth.config import MSGraphyConfig
from msgraphy.auth.graph_auth import BasicAuth
from msgraphy.client.graph_client import RequestsGraphClient

client_id = os.environ.get("O365_CLIENT_ID")
client_secret = os.environ.get("O365_CLIENT_SECRET")
tenant_id = os.environ.get("O365_TENANT_ID")

if client_id and client_secret:
    config = MSGraphyConfig(
        client_id=client_id, client_secret=client_secret, tenant_id=tenant_id
    )
    MSGRAPHY_CLIENT = RequestsGraphClient(BasicAuth(config=config))
    O365_EMAIL_SENDER = os.environ["O365_EMAIL_SENDER"]
