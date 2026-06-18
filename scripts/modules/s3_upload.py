import os
import urllib.parse

import boto3
import streamlit as st
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.env"
load_dotenv(_CONFIG_PATH)
load_dotenv()


def _get_s3_client():
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    if aws_access_key_id and aws_secret_access_key:
        boto3.setup_default_session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
    return boto3.client("s3")


def upload_to_s3(file_obj, bucket_name, s3_file_name):
    s3 = _get_s3_client()
    try:
        file_obj.seek(0)
        s3.upload_fileobj(file_obj, bucket_name, s3_file_name)
        return True
    except NoCredentialsError:
        st.error("AWS credentials not available")
        return False
    except Exception as exc:
        st.error(f"An error occurred while uploading: {exc}")
        return False


def build_s3_file_url(bucket_name, folder_name, file_name):
    encoded_folder = urllib.parse.quote(folder_name)
    encoded_file = urllib.parse.quote(file_name)
    return (
        f"https://{bucket_name}.s3.ap-south-1.amazonaws.com/"
        f"{encoded_folder}/{encoded_file}"
    )
