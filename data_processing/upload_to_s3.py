import boto3
from fastapi import FastAPI, UploadFile, File, HTTPException
from botocore.exceptions import ClientError

app = FastAPI()


s3_client = boto3.client(
    "s3",
    region_name=region_name
)


@app.post("/upload")
async def upload_file(file: UploadFile=File(...)):
    try:
        s3_client.upload_fileobj(file.file,
                          bucket_name,
                          file.filename)

        return {
                "message": "Upload successful",
                "filename": file.filename,
                "s3_key": f"uploads/{file.filename}"
            }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))
