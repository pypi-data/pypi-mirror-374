import logging

import concurrent
import boto3
from PIL import Image
from typing import Tuple
from espy_pdfier.util import CONSTANTS
from espy_pdfier.service.schema import Uploader
import os
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_greater_than_allowed_size(image_path):
    if not CONSTANTS.IMAGE_SIZE_MB:
        return False
    return os.path.getsize(image_path) > int(CONSTANTS.IMAGE_SIZE_MB) * 1024 * 1024


def is_image_size_valid(file):
    max_size_mb = float(CONSTANTS.IMAGE_SIZE_MB) * 1024 * 1024
    file_size_mb = file.file.seek(0, 2) / (1024 * 1024)  # Get file size in MB
    file.file.seek(0)  # Reset file pointer to the beginning
    return file_size_mb <= max_size_mb


def resize_image(image_bytes, max_size):
    """
    Resizes an image to the specified max size.

    Args:
        image_bytes: The image data as bytes.
        max_size: The maximum size (width, height) of the resized image.

    Returns:
        A BytesIO object containing the resized image data.
    """
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail(max_size)
    resized_image_buffer = io.BytesIO()
    image.save(resized_image_buffer, format=image.format)
    resized_image_buffer.seek(0)
    return resized_image_buffer


async def gen_presigned_url(uploader: Uploader) -> str:
    """Generates a presigned URL for accessing an object in S3.

    Args:
        bucket_name: The name of the S3 bucket.
        key: The key of the object in the S3 bucket.
        expiration: The time in seconds for which the presigned URL is valid.

    Returns:
        A presigned URL as a string.
    """
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": uploader.bucket,
                "Key": uploader.filename,
                "ContentType": uploader.filetype,
            },
            ExpiresIn=uploader.expiration,
        )
        return url
    except Exception as e:
        logging.error(f"An error occurred generating presigned URL: {str(e)}")
        raise Exception(f"An error occurred: {str(e)}.")


def check_s3_object_exists(bucket: str, key: str) -> bool:
    """Check if S3 object exists."""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except s3.exceptions.ClientError as e:
        logging.error(f"An error occurred checking S3 object existence: {str(e)}")
        return False


def store_image_in_s3(image_buffer, bucket_name, key) -> str:
    """Can be called directly to store image in S3.
    args:
    image_buffer: file.file from FastAPI file upload.
    returns:
    filename: name or key of the image in s3
    """
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        s3.upload_fileobj(image_buffer, bucket_name, key)
        return f"https://{bucket_name}.s3.amazonaws.com/{key}"
    except Exception as e:
        logging.error(f"An error occured uploadig to s3: {str(e)}")
        raise Exception(f"An error occured: {str(e)}.")


def store_video_in_s3(image_buffer, bucket_name, key) -> str:
    """Can be called directly to store image in S3.
    args:
    image_buffer: file.file from FastAPI file upload.
    returns:
    filename: name or key of the image in s3
    """
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        s3.upload_fileobj(image_buffer, bucket_name, key)
        return f"{key}"
    except Exception as e:
        logging.error(f"An error occured uploadig to s3: {str(e)}")
        raise Exception(f"An error occured: {str(e)}.")


def store_zip_s3(zip_bytes, bucket_name, key) -> str:
    """Stores a zip directory of static content in s3."""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        s3.upload_fileobj(
            zip_bytes, bucket_name, key, ExtraArgs={"ACL": "private"}
        )  # read only zip
        return f"https://essl.b-cdn.net/{key}"
    except Exception as e:
        logging.error(f"An error occured uploadig to s3: {str(e)}")
        raise Exception(f"An error occured: {str(e)}.")


def resize_and_store_images(
    image,
    bucket_name: str,
    thumbnail_size: Tuple[int, int] = (100, 100),
    display_size: Tuple[int, int] = (512, 512),
) -> dict[str, str]:
    """Resizes image (only) to thumbnail and display image while still keeping raw."""
    try:
        if not is_image_size_valid(image):
            raise ValueError("Image size exceeds the allowed limit.")
        name = image.filename
        raw_name = f"raw_{image.filename}"

        store_image_in_s3(image.file, bucket_name, raw_name)

        thumbnail_image = resize_image(image, thumbnail_size)
        display_image = resize_image(image, display_size)

        filename_thumb = f"thumb_{name}"
        store_image_in_s3(thumbnail_image, bucket_name, filename_thumb)

        filename_dp = f"dp_{name}"
        store_image_in_s3(display_image, bucket_name, filename_dp)
        return {
            "thumbnail": f"https://{bucket_name}.s3.amazonaws.com/{filename_thumb}",
            "dp": f"https://{bucket_name}.s3.amazonaws.com/{filename_dp}",
            "raw": f"https://{bucket_name}.s3.amazonaws.com/{raw_name}",
        }

    except Exception as e:
        logging.error(f"An error occurred resizing and storing: {str(e)}")
        raise Exception(f"An error occurred: {str(e)}.")


def delete_s3(bucket_name: str, key: str) -> None:
    """Deletes an object from S3."""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        s3.delete_object(Bucket=bucket_name, Key=key)
    except Exception as e:
        logging.error(f"An error occurred deleting from S3: {str(e)}")
        raise Exception(f"An error occurred: {str(e)}.")


def get_s3_object(bucket_name: str, key: str) -> bytes:
    """Retrieves an object from S3."""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        response = s3.get_object(Bucket=bucket_name, Key=key)
        return response["Body"].read()
    except Exception as e:
        logging.error(f"An error occurred retrieving from S3: {str(e)} for key {key}")
        raise Exception(f"An error occurred: {str(e)}.")


def get_multiple_s3_objects(bucket_name: str, keys: list[str]) -> dict[str, bytes]:
    """Retrieves multiple objects from S3 using threading."""

    def get_single_object(key: str) -> tuple:
        try:
            data = get_s3_object(bucket_name, key)
            return key, data
        except Exception as e:
            logging.error(f"Error retrieving {key}: {str(e)}")
            return key, None

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_key = {executor.submit(get_single_object, key): key for key in keys}
        results = {}

        for future in concurrent.futures.as_completed(future_to_key):
            key, data = future.result()
            if data is not None:
                results[key] = data

    return results


def get_s3_object_stream(bucket_name: str, key: str, range_header: str = None):
    """Retrieves an S3 object for streaming."""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )

        get_object_params = {"Bucket": bucket_name, "Key": key}
        if range_header:
            get_object_params["Range"] = range_header

        response = s3.get_object(**get_object_params)
        return response

    except Exception as e:
        logging.error(f"An error occurred retrieving from S3: {str(e)} for key {key}")
        raise Exception(f"An error occurred: {str(e)}.")


def get_s3_object_metadata(bucket_name: str, key: str):
    """Get S3 object metadata."""
    try:
        s3 = boto3.client(
            "s3",
            aws_access_key_id=CONSTANTS.S3_KEY,
            aws_secret_access_key=CONSTANTS.S3_SECRET,
        )
        return s3.head_object(Bucket=bucket_name, Key=key)
    except Exception as e:
        logging.error(
            f"An error occurred getting metadata from S3: {str(e)} for key {key}"
        )
        return None
