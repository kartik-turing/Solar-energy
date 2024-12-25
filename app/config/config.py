import json
from app.config.secrets_manager import fetch_and_store_secrets

class SecretsInstance(object):
    def __init__(self, secrets):
        for key, value in secrets.items():
            setattr(self, key, json.loads(value)) if key == "AURORA_TOKENS" else setattr(self,key,value)

secrets_collection = fetch_and_store_secrets()
SECRETS = SecretsInstance(secrets_collection)