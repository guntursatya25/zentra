from datetime import datetime

from pydantic import BaseModel


class DocumentCategoryOut(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentCategoryCreate(BaseModel):
    name: str
    description: str | None = None


class DocumentOut(BaseModel):
    id: str
    title: str
    description: str | None
    category_id: int | None
    file_type: str
    file_size: int | None
    version: int
    status: str
    is_latest_version: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListOut(BaseModel):
    id: str
    title: str
    category_id: int | None
    category_name: str | None
    file_type: str
    version: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChunkUpdate(BaseModel):
    bab: str | None = None
    bab_judul: str | None = None
    pasal: str | None = None
    pasal_judul: str | None = None
    ayat: str | None = None


class ChunkOutWithDoc(BaseModel):
    id: str
    bab: str | None
    bab_judul: str | None
    pasal: str | None
    pasal_judul: str | None
    ayat: str | None
    teks: str
    halaman: int | None
    chunk_index: int
    document_title: str | None
