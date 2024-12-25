import json
import logging
import os

import boto3
import botocore
import botocore.session
from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

in_memory_secrets = {}

secret_name_dev = "sim-secrets-dev"
secret_name_rds_dev = "rds_postgres_secret"
secret_name_rds_prod = "rds_postgres_secret"
secret_name_prod = "sim-secrets-dev"
secret_names_collection = {
    "development": [secret_name_dev, secret_name_rds_dev],
    "production": [secret_name_prod, secret_name_rds_prod],
}

toml_file = "app/config/settings.toml"
secret_key = "secrets_collection"
in_memory = {}


def fetch_secrets(env):
    secrets_all = {}
        
    for secret_name in secret_names_collection[env]:
        try:
            client = botocore.session.get_session().create_client(
                "secretsmanager"
            )
            cache_config = SecretCacheConfig()
            cache = SecretCache(config=cache_config, client=client)
            secret_value = cache.get_secret_string(secret_name)
            secrets_all[secret_name] = secret_value
        except Exception as e:
            logging.error(f"Error fetching secret {secret_name}: {str(e)}")
            secrets_all[secret_name] = None
    secrets = {}
    for key, value in secrets_all.items():
        values_dict = dict()
        if isinstance(value, str):
            values_dict = json.loads(value)
        elif isinstance(value, dict):
            values_dict = value
        else:
            raise RuntimeError("Secrets collection data type is not recognized")
        secrets.update(values_dict)
    return secrets

def fetch_and_store_secrets():
    env = "development"
    if os.getenv("YOUR_ENV"):
        env = os.getenv("YOUR_ENV")
    if secret_key in in_memory:
        return in_memory[secret_key]

    secret_value = fetch_secrets(env)
    # Store secrets in memory
    in_memory[secret_key] = secret_value
    return secret_value

