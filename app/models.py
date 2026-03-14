from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, UniqueConstraint


# Database models for PostgreSQL
class Account(SQLModel, table=True):
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    account_id: int | None = Field(default=None, primary_key=True)
    account_number: str
    financial_institution: str
    account_name: str
    account_owner: str | None = None
    active: bool = True
    comments: str | None = None
    account_type: str | None = None


class Transaction(SQLModel, table=True):
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    transaction_id: int | None = Field(default=None, primary_key=True)
    transaction_date: datetime
    transaction_type: str | None = None
    transaction_amount: float
    merchant: str | None = None
    category: str | None = None
    account_id: int = Field(foreign_key='account.account_id')
    cycle_id: int | None = Field(default=None, foreign_key='cycle.cycle_id')
    email_id: int | None = Field(default=None, foreign_key='email.email_id')
    file_id: int | None = Field(default=None, foreign_key='file.file_id')
    expense_owner: str | None = None
    llm_reasoning: str | None = None
    comment: str | None = None
    updated_by: str | None = None
    updated_at: datetime | None = None
    is_budgeted: bool = False
    is_deleted: bool = False


class Email(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint(
            'email_uid', 'folder', 'from_address', 'to_address', 'email_date'
        ),
    )
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    email_id: int | None = Field(default=None, primary_key=True)
    email_uid: int
    folder: str
    from_address: str | None = None
    to_address: str | None = None
    email_date: datetime | None = None


class File(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('file_name', 'file_path'),)
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    file_id: int | None = Field(default=None, primary_key=True)
    file_name: str
    file_path: str
    file_created_at: datetime | None = None


class Cycle(SQLModel, table=True):
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    cycle_id: int | None = Field(default=None, primary_key=True)
    cycle_start: datetime
    cycle_end: datetime
    cycle_description: str | None = None
    comments: str | None = None


class EmailCheckpoint(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('folder'),)
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    id: int | None = Field(default=None, primary_key=True)
    folder: str
    last_seen_uid: int


class Checkpoint(SQLModel, table=True):
    __table_args__ = (UniqueConstraint('identifier'),)
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    id: int | None = Field(default=None, primary_key=True)
    identifier: str
    checkpoint: str


class Category(SQLModel, table=True):
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    category_id: int | None = Field(default=None, primary_key=True)
    category_name: str
    category_description: str | None = None
    comments: str | None = None


class Merchant(SQLModel, table=True):
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None
    merchant_id: int | None = Field(default=None, primary_key=True)
    merchant_name: str
    merchant_description: str | None = None
    comments: str | None = None


# API request/response models
class TransactionRequest(BaseModel):
    load_by: str | None = None
    transaction_date: datetime
    transaction_type: str | None = None
    transaction_amount: float
    merchant: str | None = None
    category: str | None = None
    account_id: int
    cycle_id: int | None = None
    email_id: int | None = None
    file_id: int | None = None
    expense_owner: str | None = None
    llm_reasoning: str | None = None
    comment: str | None = None
    updated_by: str | None = None
    updated_at: datetime | None = None
    is_budgeted: bool
    is_deleted: bool


class TransactionResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    transaction_date: datetime
    transaction_type: str | None = None
    transaction_amount: float
    merchant: str | None = None
    category: str | None = None
    account_id: int
    cycle_id: int | None = None
    email_id: int | None = None
    file_id: int | None = None
    expense_owner: str | None = None
    llm_reasoning: str | None = None
    comment: str | None = None
    updated_by: str | None = None
    updated_at: datetime | None = None
    is_budgeted: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class AccountRequest(BaseModel):
    load_by: str | None = None
    account_number: str
    financial_institution: str
    account_name: str
    account_owner: str | None = None
    active: bool = True
    comments: str | None = None
    account_type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AccountResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    account_id: int
    account_number: str
    financial_institution: str
    account_name: str
    account_owner: str | None = None
    active: bool = True
    comments: str | None = None
    account_type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EmailCheckpointRequest(BaseModel):
    last_seen_uid: int


class EmailCheckpointCreate(BaseModel):
    folder: str
    last_seen_uid: int


class EmailCheckpointResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    id: int | None = None
    folder: str
    last_seen_uid: int | None = None

    model_config = ConfigDict(from_attributes=True)


class CheckpointRequest(BaseModel):
    checkpoint: str


class CheckpointCreate(BaseModel):
    identifier: str
    checkpoint: str


class CheckpointResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    id: int | None = None
    identifier: str
    checkpoint: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CycleRequest(BaseModel):
    load_by: str | None = None
    cycle_start: datetime
    cycle_end: datetime
    cycle_description: str | None = None
    comments: str | None = None


class CycleResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    cycle_id: int
    cycle_start: datetime
    cycle_end: datetime
    cycle_description: str | None = None
    comments: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CycleIdResponse(BaseModel):
    cycle_id: int | None = None


class AccountIdResponse(BaseModel):
    account_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class CategoryRequest(BaseModel):
    load_by: str | None = None
    category_name: str
    category_description: str | None = None
    comments: str | None = None


class CategoryResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    category_id: int
    category_name: str
    category_description: str | None = None
    comments: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MerchantRequest(BaseModel):
    load_by: str | None = None
    merchant_name: str
    merchant_description: str | None = None
    comments: str | None = None


class MerchantResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    merchant_id: int
    merchant_name: str
    merchant_description: str | None = None
    comments: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EmailRequest(BaseModel):
    load_by: str | None = None
    email_uid: int
    folder: str
    from_address: str | None = None
    to_address: str | None = None
    email_date: datetime | None = None


class EmailResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    email_id: int
    email_uid: int
    folder: str
    from_address: str | None = None
    to_address: str | None = None
    email_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class FileRequest(BaseModel):
    load_by: str | None = None
    file_name: str
    file_path: str
    file_created_at: datetime | None = None


class FileResponse(BaseModel):
    load_by: str | None = None
    load_time: datetime | None = None
    file_id: int
    file_name: str
    file_path: str
    file_created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
