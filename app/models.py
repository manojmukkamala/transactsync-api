from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, UniqueConstraint


# Database models for PostgreSQL
class Account(SQLModel, table=True):
    account_id: int | None = Field(default=None, primary_key=True)
    account_number: str
    financial_institution: str
    account_name: str
    account_owner: str | None = None
    active: bool = True
    comments: str | None = None
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None

class Transaction(SQLModel, table=True):
    transaction_id: int | None = Field(default=None, primary_key=True)
    transaction_date: datetime
    transaction_amount: float
    merchant: str
    account_id: int = Field(foreign_key="account.account_id")
    expense_owner: str | None = None
    from_address: str
    to_address: str
    email_uid: int
    email_date: datetime
    llm_reasoning: str | None = None
    is_deleted: bool = False
    comment: str | None = None
    updated_by: str | None = None
    updated_at: datetime | None = None
    transaction_type: str | None = None
    cycle_id: int | None = Field(default=None, foreign_key="cycle.cycle_id")
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None

class EmailCheckpoint(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("folder"),
    )    
    id: int | None = Field(default=None, primary_key=True)
    folder: str
    last_seen_uid: int
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None

class Cycle(SQLModel, table=True):
    cycle_id: int | None = Field(default=None, primary_key=True)
    cycle_start: datetime
    cycle_end: datetime
    cycle_description: str | None = None
    comments: str | None = None
    load_time: datetime = Field(default_factory=datetime.utcnow)
    load_by: str | None = None

# API request/response models
class TransactionRequest(BaseModel):
    transaction_date: datetime
    transaction_amount: float
    merchant: str
    account_id: int
    from_address: str
    to_address: str
    email_uid: int
    email_date: datetime
    transaction_type: str | None = None
    cycle_id: int | None = None

class TransactionResponse(BaseModel):
    transaction_id: int
    transaction_date: datetime
    transaction_amount: float
    merchant: str
    account_id: int
    from_address: str
    to_address: str
    email_uid: int
    email_date: datetime
    transaction_type: str | None = None
    cycle_id: int | None = None
    created_at: datetime

class AccountRequest(BaseModel):
    account_number: str
    financial_institution: str
    account_name: str
    account_owner: str | None = None
    comments: str | None = None

class AccountResponse(BaseModel):
    account_id: int
    account_number: str
    financial_institution: str
    account_name: str
    account_owner: str | None = None
    active: bool = True
    comments: str | None = None

    model_config = ConfigDict(from_attributes=True)

class CheckpointRequest(BaseModel):
    last_seen_uid: int

class CheckpointCreate(BaseModel):
    folder: str
    last_seen_uid: int

class CheckpointResponse(BaseModel):
    id: int | None = None
    folder: str
    last_seen_uid: int | None = None

    model_config = ConfigDict(from_attributes=True)

class CycleRequest(BaseModel):
    cycle_start: datetime
    cycle_end: datetime
    cycle_description: str | None = None
    comments: str | None = None

class CycleResponse(BaseModel):
    cycle_id: int
    cycle_start: datetime
    cycle_end: datetime
    cycle_description: str | None = None
    comments: str | None = None

    model_config = ConfigDict(from_attributes=True)

class CycleIdResponse(BaseModel):
    cycle_id: int | None = None
