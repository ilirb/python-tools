import os
import argparse
from datetime import datetime
from google.cloud import storage


def upload_blob(args):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
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
    storage_client = storage.Client()

    bucket = storage_client.get_bucket(args.bucket_name)
    bucket.versioning_enabled = True
    bucket.patch()

    print("Versioning was enabled for bucket {}".format(bucket.name))
    return bucket


def list_file_archived_generations(args):
    """Lists all the blobs in the bucket with generation."""
    storage_client = storage.Client()

    blobs = storage_client.list_blobs(args.bucket_name, versions=True)

    for blob in blobs:
        print("{},{},{}".format(blob.name, blob.generation, datetime.fromtimestamp(blob.generation/1000000).strftime('%c')))


if __name__ == "__main__":
    # https://docs.python.org/3/library/argparse.html
    parser = argparse.ArgumentParser(description='Google Cloud Storage')
    subparsers = parser.add_subparsers(help="")

    base_subparser = argparse.ArgumentParser(add_help=False)
    base_subparser.add_argument('--bucket_name', help='Bucket name', required=True)

    # upload
    parser_upload = subparsers.add_parser('upload', help="Upload blob", parents=[base_subparser])
    parser_upload.add_argument('--source_file', help='Path to source file', required=True)
    parser_upload.add_argument('--blob_name', help='Destination blob name', required=True)
    parser_upload.set_defaults(func=upload_blob)

    # versioning
    parser_enable_ver = subparsers.add_parser('versioning', help="Enable versioning", parents=[base_subparser])
    parser_enable_ver.set_defaults(func=enable_versioning)

    # list bucket
    parser_enable_list = subparsers.add_parser('list_archive', help="List archived file generations", parents=[base_subparser])
    parser_enable_list.set_defaults(func=list_file_archived_generations)

    args = parser.parse_args()
    args.func(args)
