#!/usr/bin/env python3

import os
import sys
import argparse
from datetime import datetime
from google.cloud import storage


def upload_blob(args):
    """Uploads a file to the bucket."""
    storage_client = storage.Client.from_service_account_json(args.credentials)

    bucket = storage_client.bucket(args.bucket_name)
    blob = bucket.blob(args.blob_name)

    blob.upload_from_filename(args.source_file)

    print(
        "File {} uploaded to {}.".format(
            args.source_file, args.blob_name
        )
    )


def enable_versioning(args):
    """Enable versioning for this bucket."""
    storage_client = storage.Client.from_service_account_json(args.credentials)

    bucket = storage_client.get_bucket(args.bucket_name)
    bucket.versioning_enabled = True
    bucket.patch()

    print("Versioning was enabled for bucket {}".format(bucket.name))
    return bucket


def list_blob(args):
    """Lists all the blobs in the bucket with generation."""
    storage_client = storage.Client.from_service_account_json(args.credentials)

    blobs = storage_client.list_blobs(args.bucket_name, versions=True)

    for blob in blobs:
        print("{},{},{}".format(blob.name, blob.generation, datetime.fromtimestamp(blob.generation/1000000).strftime('%c')))


def delete(args):
    """Delete a blob."""
    storage_client = storage.Client.from_service_account_json(args.credentials)

    bucket = storage_client.bucket(args.bucket_name)
    blob = bucket.blob(args.blob_name)

    blob.delete()

if __name__ == "__main__":
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='Google Cloud Storage')
    subparsers = parser.add_subparsers(help="")

    base_subparser = argparse.ArgumentParser(add_help=False)
    base_subparser.add_argument('--bucket_name', help='Bucket name', required=True)
    base_subparser.add_argument('--credentials', help='Credentials', default=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

    # upload
    parser_upload = subparsers.add_parser('upload', help="Upload blob", parents=[base_subparser])
    parser_upload.add_argument('--source_file', help='Path to source file', required=True)
    parser_upload.add_argument('--blob_name', help='Destination blob name', required=True)
    parser_upload.set_defaults(func=upload_blob)

    # versioning
    parser_enable_ver = subparsers.add_parser('versioning', help="Enable versioning", parents=[base_subparser])
    parser_enable_ver.set_defaults(func=enable_versioning)

    # list bucket
    parser_enable_list = subparsers.add_parser('list', help="List archived file generations", parents=[base_subparser])
    parser_enable_list.set_defaults(func=list_blob)

    # delete bucket
    parser_delete = subparsers.add_parser('delete', help="List archived file generations", parents=[base_subparser])
    parser_delete.add_argument('--blob_name', help='Blob name', required=True)
    parser_delete.set_defaults(func=delete)

    args = parser.parse_args()
    if not args.credentials:
        sys.exit("Set --credentials")
    args.func(args)
