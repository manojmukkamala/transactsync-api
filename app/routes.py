import logging
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from .db import get_async_session, init_db
from .models import (
    Account,
    AccountIdResponse,
    AccountRequest,
    AccountResponse,
    CheckpointCreate,
    CheckpointRequest,
    CheckpointResponse,
    Cycle,
    CycleIdResponse,
    CycleRequest,
    CycleResponse,
    EmailCheckpoint,
    Transaction,
    TransactionRequest,
    TransactionResponse,
)
from .security import get_api_key

# Initialize FastAPI app
app = FastAPI(
    title='TransactSync API',
    description='API for financial transaction synchronization from email alerts',
    version='1.0.0',
    dependencies=[Security(get_api_key)],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['0.0.0.0'],  # noqa: S104
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],
    allow_headers=['Authorization', 'Content-Type'],
)


# Create database tables
@app.on_event('startup')
async def startup_event() -> None:
    # This would create tables if they don't exist
    logger = logging.getLogger(__name__)
    logger.info('TransactSync API is starting up')
    await init_db()


# Health check endpoint
@app.get('/health', tags=['Health'])
async def health_check() -> dict:
    """
    Health check endpoint to verify the API is running.
    Returns:
        dict: A simple JSON response confirming the API is healthy.
    """
    return {'status': 'healthy', 'message': 'TransactSync API is running'}


# Root endpoint
@app.get('/', tags=['General'])
async def root() -> dict:
    """
    Root endpoint providing basic information about the API.
    Returns:
        dict: Information about the API.
    """
    return {
        'message': 'Welcome to TransactSync API',
        'version': '1.0.0',
        'description': 'AI powered Python app to log financial transactions by parsing email alerts',
    }


# accounts endpoints
@app.post('/accounts', tags=['Accounts'], response_model=AccountResponse)
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


@app.get('/accounts', tags=['Accounts'], response_model=list[AccountResponse])
async def get_accounts() -> list[AccountResponse]:
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


@app.get('/accounts/by-number', tags=['Accounts'], response_model=AccountIdResponse)
async def get_account_id_by_account_number(account_number: str) -> AccountIdResponse:
    """
    Resolve account_id by account_number via API.
    Args:
        account_number: The account number to look up
    Returns:
        AccountIdResponse with account_id
    """
    async with get_async_session() as session:
        statement = select(Account).where(Account.account_number == account_number)
        result = await session.execute(statement)
        account = result.scalars().one_or_none()
        if account:
            return AccountIdResponse(account_id=account.account_id)
        else:
            return AccountIdResponse(account_id=None)


@app.get('/accounts/{account_id}', tags=['Accounts'], response_model=AccountResponse)
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
            raise HTTPException(status_code=404, detail='Account not found')
        return AccountResponse.model_validate(account)


@app.put('/accounts/{account_id}', tags=['Accounts'], response_model=AccountResponse)
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
            raise HTTPException(status_code=404, detail='Account not found')

        # Update the account fields directly
        for key, value in account.model_dump().items():
            if hasattr(db_account, key):
                setattr(db_account, key, value)

        await session.commit()
        await session.refresh(db_account)
        return AccountResponse.model_validate(db_account)


@app.delete('/accounts/{account_id}', tags=['Accounts'])
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
            raise HTTPException(status_code=404, detail='Account not found')

        await session.delete(db_account)
        await session.commit()
        return {'status': 'success', 'message': 'Account deleted'}


# Cycle endpoints
@app.post('/cycles', tags=['Cycles'], response_model=CycleResponse)
async def create_cycle(payload: CycleRequest) -> CycleResponse:
    async with get_async_session() as session:
        cyc = Cycle(**payload.model_dump())
        session.add(cyc)
        await session.commit()
        await session.refresh(cyc)
        return CycleResponse.model_validate(cyc)


@app.get('/cycles', tags=['Cycles'], response_model=list[CycleResponse])
async def get_cycles() -> list[CycleResponse]:
    async with get_async_session() as session:
        statement = select(Cycle)
        result = await session.execute(statement)
        cycles = result.scalars().all()
        return [CycleResponse.model_validate(c) for c in cycles]


@app.get('/cycles/for-date', tags=['Cycles'], response_model=CycleIdResponse)
async def get_cycle_id_for_date(transaction_date: datetime) -> CycleIdResponse:
    """
    Return the `cycle_id` that contains the given transaction_date.
    Accepts an ISO datetime as query parameter `transaction_date`.
    """
    async with get_async_session() as session:
        statement = (
            select(Cycle)
            .where(
                Cycle.cycle_start <= transaction_date,
                Cycle.cycle_end >= transaction_date,
            )
            .limit(1)
        )
        result = await session.execute(statement)
        cyc = result.scalars().one_or_none()
        return CycleIdResponse(cycle_id=cyc.cycle_id if cyc else None)


@app.get('/cycles/{cycle_id}', tags=['Cycles'], response_model=CycleResponse)
async def get_cycle(cycle_id: int) -> CycleResponse:
    async with get_async_session() as session:
        statement = select(Cycle).where(Cycle.cycle_id == cycle_id)
        result = await session.execute(statement)
        cyc = result.scalars().one_or_none()
        if not cyc:
            raise HTTPException(status_code=404, detail='Cycle not found')
        return CycleResponse.model_validate(cyc)


@app.put('/cycles/{cycle_id}', tags=['Cycles'], response_model=CycleResponse)
async def update_cycle(cycle_id: int, payload: CycleRequest) -> CycleResponse:
    async with get_async_session() as session:
        statement = select(Cycle).where(Cycle.cycle_id == cycle_id)
        result = await session.execute(statement)
        cyc = result.scalars().one_or_none()
        if not cyc:
            raise HTTPException(status_code=404, detail='Cycle not found')

        for key, value in payload.model_dump().items():
            if hasattr(cyc, key):
                setattr(cyc, key, value)

        await session.commit()
        await session.refresh(cyc)
        return CycleResponse.model_validate(cyc)


@app.delete('/cycles/{cycle_id}', tags=['Cycles'])
async def delete_cycle(cycle_id: int) -> dict:
    async with get_async_session() as session:
        statement = select(Cycle).where(Cycle.cycle_id == cycle_id)
        result = await session.execute(statement)
        cyc = result.scalars().one_or_none()
        if not cyc:
            raise HTTPException(status_code=404, detail='Cycle not found')
        await session.delete(cyc)
        await session.commit()
        return {'status': 'success', 'message': 'Cycle deleted'}


# email_checkpoints endpoints
@app.get(
    '/email_checkpoints/{folder}',
    tags=['EmailCheckpoints'],
    response_model=CheckpointResponse,
)
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


@app.put(
    '/email_checkpoints/{folder}',
    tags=['EmailCheckpoints'],
    response_model=CheckpointResponse,
)
async def set_last_seen_uid(
    folder: str, payload: CheckpointRequest
) -> CheckpointResponse:
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


@app.post(
    '/email_checkpoints', tags=['EmailCheckpoints'], response_model=CheckpointResponse
)
async def create_email_checkpoint(payload: CheckpointCreate) -> CheckpointResponse:
    """
    Create a new email checkpoint or update if exists.
    Body: {"folder": str, "last_seen_uid": int}
    Returns:
        CheckpointResponse: Created/updated checkpoint data
    """
    async with get_async_session() as session:
        # check if already exists
        statement = select(EmailCheckpoint).where(
            EmailCheckpoint.folder == payload.folder
        )
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


@app.get(
    '/email_checkpoints',
    tags=['EmailCheckpoints'],
    response_model=list[CheckpointResponse],
)
async def get_all_email_checkpoints() -> list[CheckpointResponse]:
    """
    Get all email checkpoints.
    Returns:
        List[CheckpointResponse]: List of all checkpoints
    """
    async with get_async_session() as session:
        statement = select(EmailCheckpoint)
        result = await session.execute(statement)
        checkpoints = result.scalars().all()
        return [CheckpointResponse.model_validate(cp) for cp in checkpoints]


@app.delete('/email_checkpoints/{folder}', tags=['EmailCheckpoints'])
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
            raise HTTPException(status_code=404, detail='Email checkpoint not found')
        await session.delete(cp)
        await session.commit()
        return {
            'status': 'success',
            'message': f'Checkpoint for folder {folder} deleted',
        }


# Transaction endpoints
@app.post('/transactions', tags=['Transactions'], response_model=TransactionResponse)
async def create_transaction(payload: TransactionRequest) -> TransactionResponse:
    """
    Create a new transaction.
    """
    async with get_async_session() as session:
        txn = Transaction(**payload.model_dump())
        session.add(txn)
        await session.commit()
        await session.refresh(txn)
        return TransactionResponse.model_validate(txn)


@app.get(
    '/transactions', tags=['Transactions'], response_model=list[TransactionResponse]
)
async def get_transactions(
    start_date: str | None = None,
    end_date: str | None = None,
    cycle_id: int | None = None,
) -> list[TransactionResponse]:
    """
    Get all transactions.
    Optionally filter by start_date, end_date, and cycle_id.
    """
    async with get_async_session() as session:
        statement = select(Transaction)

        # Apply filters if provided
        if start_date is not None:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')  # noqa: DTZ007
            statement = statement.where(Transaction.transaction_date >= start_date_obj)
        if end_date is not None:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)  # noqa: DTZ007
            statement = statement.where(Transaction.transaction_date <= end_date_obj)
        if cycle_id is not None:
            statement = statement.where(Transaction.cycle_id == cycle_id)

        result = await session.execute(statement)
        transactions = result.scalars().all()
        return [TransactionResponse.model_validate(t) for t in transactions]


@app.get(
    '/transactions/{transaction_id}',
    tags=['Transactions'],
    response_model=TransactionResponse,
)
async def get_transaction(transaction_id: int) -> TransactionResponse:
    """
    Get a transaction by ID.
    """
    async with get_async_session() as session:
        statement = select(Transaction).where(
            Transaction.transaction_id == transaction_id
        )
        result = await session.execute(statement)
        txn = result.scalars().one_or_none()
        if not txn:
            raise HTTPException(status_code=404, detail='Transaction not found')
        return TransactionResponse.model_validate(txn)


@app.put(
    '/transactions/{transaction_id}',
    tags=['Transactions'],
    response_model=TransactionResponse,
)
async def update_transaction(
    transaction_id: int, payload: TransactionRequest
) -> TransactionResponse:
    """
    Update a transaction.
    """
    async with get_async_session() as session:
        statement = select(Transaction).where(
            Transaction.transaction_id == transaction_id
        )
        result = await session.execute(statement)
        txn = result.scalars().one_or_none()
        if not txn:
            raise HTTPException(status_code=404, detail='Transaction not found')

        for key, value in payload.model_dump().items():
            if hasattr(txn, key):
                setattr(txn, key, value)

        await session.commit()
        await session.refresh(txn)
        return TransactionResponse.model_validate(txn)


@app.delete('/transactions/{transaction_id}', tags=['Transactions'])
async def delete_transaction(transaction_id: int) -> dict:
    """
    Delete a transaction.
    """
    async with get_async_session() as session:
        statement = select(Transaction).where(
            Transaction.transaction_id == transaction_id
        )
        result = await session.execute(statement)
        txn = result.scalars().one_or_none()
        if not txn:
            raise HTTPException(status_code=404, detail='Transaction not found')
        await session.delete(txn)
        await session.commit()
        return {'status': 'success', 'message': 'Transaction deleted'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
