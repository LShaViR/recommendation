import boto3
from fastapi import APIRouter, UploadFile, HTTPException
from botocore.exceptions import NoCredentialsError

from app.api.deps import CurrentUser
from app.core.config import settings


router = APIRouter(prefix="/utils", tags=["utils"])


VULTR_ACCESS_KEY = settings.VULTR_ACCESS_KEY
VULTR_SECRET_KEY = settings.VULTR_SECRET_KEY
VULTR_BUCKET_NAME = settings.VULTR_BUCKET_NAME
VULTR_REGION = settings.VULTR_REGION  # e.g., ewr1, sgp1, ams1
VULTR_ENDPOINT = f"https://{VULTR_REGION}.vultrobjects.com"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=VULTR_ACCESS_KEY,
    aws_secret_access_key=VULTR_SECRET_KEY,
    endpoint_url=VULTR_ENDPOINT,
)


@router.post("/upload-image/")
async def upload_image(file: UploadFile, file_name: str, current_user: CurrentUser):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        formated_file_name = f"{file_name}.{file.filename.split('.')[-1]}"
        s3_client.upload_fileobj(
            file.file,
            VULTR_BUCKET_NAME,
            formated_file_name,
            ExtraArgs={"ContentType": file.content_type, "ACL": "public-read"},
        )

        file_path = f"{VULTR_BUCKET_NAME}/{formated_file_name}"

        return {
            "message": "Upload successful",
            "filename": file.filename,
            "path": file_path,
        }

    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="Credentials not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-check/")
async def health_check() -> bool:
    return True
