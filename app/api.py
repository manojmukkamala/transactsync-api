import logging

from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from .db import get_async_session, init_db
from .models import Account, AccountRequest, AccountResponse, EmailCheckpoint, CheckpointRequest, CheckpointCreate, CheckpointResponse, CheckpointsListResponse

# Initialize FastAPI app
app = FastAPI(
    title="TransactSync API",
    description="API for financial transaction synchronization from email alerts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
async def startup_event() -> None:
    # This would create tables if they don't exist
    logger = logging.getLogger(__name__)
    logger.info("TransactSync API is starting up")
    await init_db()

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint to verify the API is running.
    Returns:
        dict: A simple JSON response confirming the API is healthy.
    """
    return {"status": "healthy", "message": "TransactSync API is running"}

# Root endpoint
@app.get("/", tags=["General"])
async def root() -> dict:
    """
    Root endpoint providing basic information about the API.
    Returns:
        dict: Information about the API.
    """
    return {
        "message": "Welcome to TransactSync API",
        "version": "1.0.0",
        "description": "AI powered Python app to log financial transactions by parsing email alerts"
    }

# accounts endpoints
@app.post("/accounts", tags=["Accounts"])
async def create_account(account: AccountRequest) -> AccountResponse:
    """
    Create a new account.
    Args:
        account: Account data to create
    Returns:
        Created account data
    """
    async with get_async_session() as session:
        db_account = Account(**account.model_dump())
        session.add(db_account)
        await session.commit()
        await session.refresh(db_account)
        return AccountResponse.model_validate(db_account)

@app.get("/accounts", tags=["Accounts"], response_model=List[AccountResponse])
async def get_accounts() -> List[AccountResponse]:
    """
    Get all accounts.
    Returns:
        List of all accounts
    """
    async with get_async_session() as session:
        statement = select(Account)
        result = await session.execute(statement)
        accounts = result.scalars().all()  # extract the Account objects
        return [AccountResponse.model_validate(acc) for acc in accounts]

@app.get("/accounts/{account_id}", tags=["Accounts"], response_model=AccountResponse)
async def get_account(account_id: int) -> AccountResponse:
    """
    Get an account by ID.
    Args:
        account_id: ID of the account to retrieve
    Returns:
        Account data
    """
    async with get_async_session() as session:
        statement = select(Account).where(Account.account_id == account_id)
        result = await session.execute(statement)
        account = result.scalars().one_or_none()      
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return AccountResponse.model_validate(account)

@app.put("/accounts/{account_id}", tags=["Accounts"], response_model=AccountResponse)
async def update_account(account_id: int, account: AccountRequest) -> AccountResponse:
    """
    Update an account.
    Args:
        account_id: ID of the account to update
        account: Updated account data
    Returns:
        Updated account data
    """
    async with get_async_session() as session:
        statement = select(Account).where(Account.account_id == account_id)
        result = await session.execute(statement)
        db_account = result.scalars().one_or_none()
        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Update the account fields directly
        for key, value in account.model_dump().items():
            if hasattr(db_account, key):
                setattr(db_account, key, value)

        await session.commit()
        await session.refresh(db_account)
        return AccountResponse.model_validate(db_account)

@app.delete("/accounts/{account_id}", tags=["Accounts"])
async def delete_account(account_id: int) -> dict:
    """
    Delete an account.
    Args:
        account_id: ID of the account to delete
    Returns:
        Deletion status
    """
    async with get_async_session() as session:
        statement = select(Account).where(Account.account_id == account_id)
        result = await session.execute(statement)
        db_account = result.scalar_one_or_none()
        if not db_account:
            raise HTTPException(status_code=404, detail="Account not found")

        await session.delete(db_account)
        await session.commit()
        return {"status": "success", "message": "Account deleted"}

# email_checkpoints endpoints
@app.get("/email_checkpoints/{folder}", tags=["EmailCheckpoints"], response_model=CheckpointResponse)
async def get_last_seen_uid(folder: str) -> CheckpointResponse:
    """
    Retrieve the last seen email UID for a specific folder.
    Returns:
        CheckpointResponse: Checkpoint data with folder and last_seen_uid
    """
    async with get_async_session() as session:
        statement = select(EmailCheckpoint).where(EmailCheckpoint.folder == folder)
        result = await session.execute(statement)
        cp = result.scalars().one_or_none()
        if cp:
            return CheckpointResponse.model_validate(cp)
        else:
            return CheckpointResponse(folder=folder, last_seen_uid=None)

@app.put("/email_checkpoints/{folder}", tags=["EmailCheckpoints"], response_model=CheckpointResponse)
async def set_last_seen_uid(folder: str, payload: CheckpointRequest) -> CheckpointResponse:
    """
    Update or insert the last seen email UID for a specific folder.
    Body:
        payload.last_seen_uid (int): UID to store
    Returns:
        CheckpointResponse: Updated checkpoint data
    """
    async with get_async_session() as session:
        statement = select(EmailCheckpoint).where(EmailCheckpoint.folder == folder)
        result = await session.execute(statement)
        cp = result.scalars().one_or_none()

        if cp:
            cp.last_seen_uid = payload.last_seen_uid
            await session.commit()
            await session.refresh(cp)
            return CheckpointResponse.model_validate(cp)
        else:
            cp = EmailCheckpoint(folder=folder, last_seen_uid=payload.last_seen_uid)
            session.add(cp)
            await session.commit()
            await session.refresh(cp)
            return CheckpointResponse.model_validate(cp)

@app.post("/email_checkpoints", tags=["EmailCheckpoints"], response_model=CheckpointResponse)
async def create_email_checkpoint(payload: CheckpointCreate) -> CheckpointResponse:
    """
    Create a new email checkpoint or update if exists.
    Body: {"folder": str, "last_seen_uid": int}
    Returns:
        CheckpointResponse: Created/updated checkpoint data
    """
    async with get_async_session() as session:
        # check if already exists
        statement = select(EmailCheckpoint).where(EmailCheckpoint.folder == payload.folder)
        result = await session.execute(statement)
        existing = result.scalars().one_or_none()
        if existing:
            # If exists, update value and return
            existing.last_seen_uid = payload.last_seen_uid
            await session.commit()
            await session.refresh(existing)
            return CheckpointResponse.model_validate(existing)

        cp = EmailCheckpoint(folder=payload.folder, last_seen_uid=payload.last_seen_uid)
        session.add(cp)
        await session.commit()
        await session.refresh(cp)
        return CheckpointResponse.model_validate(cp)

@app.get("/email_checkpoints", tags=["EmailCheckpoints"], response_model=CheckpointsListResponse)
async def get_all_email_checkpoints() -> CheckpointsListResponse:
    """
    Get all email checkpoints.
    Returns:
        CheckpointsListResponse: List of all checkpoints
    """
    async with get_async_session() as session:
        statement = select(EmailCheckpoint)
        result = await session.execute(statement)
        checkpoints = result.scalars().all()
        return CheckpointsListResponse(
            checkpoints=[CheckpointResponse.model_validate(cp) for cp in checkpoints]
        )

@app.delete("/email_checkpoints/{folder}", tags=["EmailCheckpoints"])
async def delete_email_checkpoint(folder: str) -> dict:
    """
    Delete an email checkpoint by folder.
    Returns a status dict.
    """
    async with get_async_session() as session:
        statement = select(EmailCheckpoint).where(EmailCheckpoint.folder == folder)
        result = await session.execute(statement)
        cp = result.scalars().one_or_none()
        if not cp:
            raise HTTPException(status_code=404, detail="Email checkpoint not found")
        await session.delete(cp)
        await session.commit()
        return {"status": "success", "message": f"Checkpoint for folder {folder} deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)