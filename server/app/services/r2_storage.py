"""
Cloudflare R2 Storage Service

提供 R2 对象存储的上传功能，支持 dashboard 图片等文件的云端存储
"""

import logging
import os
from typing import Optional  # noqa: F401

logger = logging.getLogger(__name__)


def is_r2_configured() -> bool:
    """检查 R2 是否已配置必要的环境变量"""
    r2_account_id = os.getenv("R2_ACCOUNT_ID")
    r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    return all([r2_account_id, r2_access_key, r2_secret_key])


def get_r2_client():
    """
    获取配置好的 boto3 S3 client 用于 R2 操作
    
    Returns:
        boto3 S3 client 或 None (如果未配置)
    """
    if not is_r2_configured():
        return None
    
    import boto3
    
    r2_account_id = os.getenv("R2_ACCOUNT_ID")
    r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    
    return boto3.client(
        's3',
        endpoint_url=f'https://{r2_account_id}.r2.cloudflarestorage.com',
        aws_access_key_id=r2_access_key,
        aws_secret_access_key=r2_secret_key,
    )


def upload_to_r2(
    data: bytes,
    key: str,
    content_type: str = "application/octet-stream",
    cache_control: str = "max-age=60"
) -> bool:
    """
    上传数据到 Cloudflare R2
    
    Args:
        data: 要上传的字节数据
        key: R2 中的文件路径/名称
        content_type: MIME 类型
        cache_control: 缓存控制头
        
    Returns:
        bool: 上传是否成功
    """
    client = get_r2_client()
    if client is None:
        logger.warning("R2 credentials not configured, skipping upload")
        return False
    
    bucket_name = os.getenv("R2_BUCKET_NAME", "file")
    
    try:
        client.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
            CacheControl=cache_control
        )
        logger.info(f"Successfully uploaded {key} to R2 bucket: {bucket_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to upload {key} to R2: {str(e)}")
        return False


def upload_dashboard_image(png_bytes: bytes) -> bool:
    """
    上传 dashboard 图片到 R2
    
    Args:
        png_bytes: PNG 图片的字节数据
        
    Returns:
        bool: 上传是否成功
    """
    return upload_to_r2(
        data=png_bytes,
        key="dashboard.png",
        content_type="image/png",
        cache_control="max-age=60"
    )
