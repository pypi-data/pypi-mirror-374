# dataplug_ui/aws_utils.py

import os
import json
import logging
from typing import Optional, Dict, List, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dataplug.cloudobject import CloudObject

logger = logging.getLogger(__name__)

def configure_aws_env(
    access_key: Optional[str],
    secret_key: Optional[str],
    region: Optional[str],
) -> None:
    """
    Set AWS credentials and region as environment variables if provided.
    """
    if access_key:
        os.environ["AWS_ACCESS_KEY_ID"] = access_key
    if secret_key:
        os.environ["AWS_SECRET_ACCESS_KEY"] = secret_key
    if region:
        os.environ["AWS_DEFAULT_REGION"] = region

def list_buckets(client: Optional[boto3.client] = None) -> List[str]:
    """
    Return a list of all S3 bucket names.
    If a boto3 client is passed, uses it; otherwise creates a new one.
    """
    if client is None:
        client = boto3.client("s3")
    try:
        resp = client.list_buckets()
        return [b["Name"] for b in resp.get("Buckets", [])]
    except (BotoCoreError, ClientError) as e:
        logger.error("Error listing S3 buckets: %s", e)
        return []

def list_files(bucket: str, prefix: str = "", delimiter: str = "") -> List[str]:
    """
    List all object keys (and common prefixes) under the given bucket/prefix.
    """
    client = boto3.client("s3")
    try:
        paginator = client.get_paginator("list_objects_v2")
        params = {"Bucket": bucket, "Prefix": prefix}
        if delimiter:
            params["Delimiter"] = delimiter

        results: List[str] = []
        for page in paginator.paginate(**params):
            # regular objects
            for obj in page.get("Contents", []):
                key = obj.get("Key", "")
                if key and not key.endswith("/"):
                    results.append(key)
            # 'directories'
            for cp in page.get("CommonPrefixes", []):
                prefix = cp.get("Prefix")
                if prefix:
                    results.append(prefix)
        return results

    except (BotoCoreError, ClientError) as e:
        logger.error("Error listing files in s3://%s/%s: %s", bucket, prefix, e)
        return []

def parse_s3_uri(s3_uri: str) -> Tuple[str, str]:
    """
    Split an S3 URI into (bucket, prefix).
    Raises ValueError on invalid format.
    """
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {s3_uri}")
    path = s3_uri[5:]
    parts = path.split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix

def parse_s3_arn(arn: str) -> Optional[str]:
    """
    Convert an S3 ARN (arn:aws:s3:::bucket/path) into an s3:// URI.
    Returns None on invalid ARN.
    """
    prefix = "arn:aws:s3:::"
    if arn.startswith(prefix):
        s3_path = arn[len(prefix):]
        uri = f"s3://{s3_path}"
        return uri if uri.endswith("/") else uri + "/"
    logger.warning("Invalid S3 ARN: %s", arn)
    return None

def load_public_datasets(base_dir: str) -> Dict:
    """
    Load the JSON file of public datasets shipped with the package.
    Returns an empty dict if missing or on parse errors.
    """
    path = os.path.join(base_dir, "data", "public_datasets_dict.json")
    if not os.path.isfile(path):
        logger.warning("Public datasets file not found: %s", path)
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        logger.error("Error loading public datasets JSON: %s", e)
        return {}

def make_cloud_object(fmt: type, uri: str) -> Optional[CloudObject]:
    """
    Instantiate a CloudObject from S3, returning None on errors.
    """
    try:
        session = boto3.Session()
        creds = session.get_credentials().get_frozen_credentials()
        s3_config = {
            "credentials": {
                "AccessKeyId": creds.access_key,
                "SecretAccessKey": creds.secret_key,
                "SessionToken": creds.token,
            },
            "region_name": session.region_name,
        }
        return CloudObject.from_s3(fmt, uri, s3_config=s3_config)
    except Exception as e:
        logger.error("Error creating CloudObject for %s: %s", uri, e)
        return None
