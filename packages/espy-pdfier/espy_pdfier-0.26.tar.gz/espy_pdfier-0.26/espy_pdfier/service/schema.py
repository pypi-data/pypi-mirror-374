from pydantic import BaseModel


class Uploader(BaseModel):
    filename: str
    filetype: str
    bucket: str | None = None
    expiration: int | None = None
