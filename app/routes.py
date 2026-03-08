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
    Checkpoint,
    CheckpointCreate,
    CheckpointRequest,
    CheckpointResponse,
    Cycle,
    CycleIdResponse,
    CycleRequest,
    CycleResponse,
    EmailCheckpoint,
    EmailCheckpointCreate,
    EmailCheckpointRequest,
    EmailCheckpointResponse,
    Transaction,
    TransactionRequest,
    TransactionResponse,
    Category,
    CategoryRequest,
    CategoryResponse,
    Merchant,
    MerchantRequest,
    MerchantResponse,
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
    response_model=EmailCheckpointResponse,
)
async def get_last_seen_uid(folder: str) -> EmailCheckpointResponse:
    """
    Retrieve the last seen email UID for a specific folder.
    Returns:
        EmailCheckpointResponse: Checkpoint data with folder and last_seen_uid
    """
    async with get_async_session() as session:
        statement = select(EmailCheckpoint).where(EmailCheckpoint.folder == folder)
        result = await session.execute(statement)
        cp = result.scalars().one_or_none()
        if cp:
            return EmailCheckpointResponse.model_validate(cp)
        else:
            return EmailCheckpointResponse(folder=folder, last_seen_uid=None)


@app.get(
    '/email_checkpoints',
    tags=['EmailCheckpoints'],
    response_model=list[EmailCheckpointResponse],
)
async def get_all_email_checkpoints() -> list[EmailCheckpointResponse]:
    """
    Get all email checkpoints.
    Returns:
        List[EmailCheckpointResponse]: List of all checkpoints
    """
    async with get_async_session() as session:
        statement = select(EmailCheckpoint)
        result = await session.execute(statement)
        checkpoints = result.scalars().all()
        return [EmailCheckpointResponse.model_validate(cp) for cp in checkpoints]


@app.put(
    '/email_checkpoints/{folder}',
    tags=['EmailCheckpoints'],
    response_model=EmailCheckpointResponse,
)
async def set_last_seen_uid(
    folder: str, payload: EmailCheckpointRequest
) -> EmailCheckpointResponse:
    """
    Update or insert the last seen email UID for a specific folder.
    Body:
        payload.last_seen_uid (int): UID to store
    Returns:
        EmailCheckpointResponse: Updated checkpoint data
    """
    async with get_async_session() as session:
        statement = select(EmailCheckpoint).where(EmailCheckpoint.folder == folder)
        result = await session.execute(statement)
        cp = result.scalars().one_or_none()

        if cp:
            cp.last_seen_uid = payload.last_seen_uid
            await session.commit()
            await session.refresh(cp)
            return EmailCheckpointResponse.model_validate(cp)
        else:
            cp = EmailCheckpoint(folder=folder, last_seen_uid=payload.last_seen_uid)
            session.add(cp)
            await session.commit()
            await session.refresh(cp)
            return EmailCheckpointResponse.model_validate(cp)


@app.post(
    '/email_checkpoints',
    tags=['EmailCheckpoints'],
    response_model=EmailCheckpointResponse,
)
async def create_email_checkpoint(
    payload: EmailCheckpointCreate,
) -> EmailCheckpointResponse:
    """
    Create a new email checkpoint or update if exists.
    Body: {"folder": str, "last_seen_uid": int}
    Returns:
        EmailCheckpointResponse: Created/updated checkpoint data
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
            return EmailCheckpointResponse.model_validate(existing)

        cp = EmailCheckpoint(folder=payload.folder, last_seen_uid=payload.last_seen_uid)
        session.add(cp)
        await session.commit()
        await session.refresh(cp)
        return EmailCheckpointResponse.model_validate(cp)


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


# checkpoints endpoints
@app.get(
    '/checkpoints/{identifier}',
    tags=['Checkpoints'],
    response_model=CheckpointResponse,
)
async def get_latest_checkpoint(identifier: str) -> CheckpointResponse:
    """
    Retrieve the latest checkpoint for a specific identifier.
    Returns:
        CheckpointResponse: Checkpoint data with identifier and checkpoint
    """
    async with get_async_session() as session:
        statement = select(Checkpoint).where(Checkpoint.identifier == identifier)
        result = await session.execute(statement)
        cp = result.scalars().one_or_none()
        if cp:
            return CheckpointResponse.model_validate(cp)
        else:
            return CheckpointResponse(identifier=identifier, checkpoint=None)


@app.get(
    '/checkpoints',
    tags=['Checkpoints'],
    response_model=list[CheckpointResponse],
)
async def get_all_checkpoints() -> list[CheckpointResponse]:
    """
    Get all  checkpoints.
    Returns:
        List[CheckpointResponse]: List of all checkpoints
    """
    async with get_async_session() as session:
        statement = select(Checkpoint)
        result = await session.execute(statement)
        checkpoints = result.scalars().all()
        return [CheckpointResponse.model_validate(cp) for cp in checkpoints]


@app.put(
    '/checkpoints/{identifier}',
    tags=['Checkpoints'],
    response_model=CheckpointResponse,
)
async def set_latest_checkpoint(
    identifier: str, payload: CheckpointRequest
) -> CheckpointResponse:
    """
    Update or insert the latest checkpoint for a specific identifier.
    Body:
        payload.checkpoint (str): checkpoint to store
    Returns:
        CheckpointResponse: Updated checkpoint data
    """
    async with get_async_session() as session:
        statement = select(Checkpoint).where(Checkpoint.identifier == identifier)
        result = await session.execute(statement)
        cp = result.scalars().one_or_none()

        if cp:
            cp.checkpoint = payload.checkpoint
            await session.commit()
            await session.refresh(cp)
            return CheckpointResponse.model_validate(cp)
        else:
            cp = Checkpoint(identifier=identifier, checkpoint=payload.checkpoint)
            session.add(cp)
            await session.commit()
            await session.refresh(cp)
            return CheckpointResponse.model_validate(cp)


@app.post(
    '/checkpoints',
    tags=['Checkpoints'],
    response_model=CheckpointResponse,
)
async def create_checkpoint(
    payload: CheckpointCreate,
) -> CheckpointResponse:
    """
    Create a new  checkpoint or update if exists.
    Body: {"identifier": str, "checkpoint": str}
    Returns:
        CheckpointResponse: Created/updated checkpoint data
    """
    async with get_async_session() as session:
        # check if already exists
        statement = select(Checkpoint).where(
            Checkpoint.identifier == payload.identifier
        )
        result = await session.execute(statement)
        existing = result.scalars().one_or_none()
        if existing:
            # If exists, update value and return
            existing.checkpoint = payload.checkpoint
            await session.commit()
            await session.refresh(existing)
            return CheckpointResponse.model_validate(existing)

        cp = Checkpoint(identifier=payload.identifier, checkpoint=payload.checkpoint)
        session.add(cp)
        await session.commit()
        await session.refresh(cp)
        return CheckpointResponse.model_validate(cp)


@app.delete('/checkpoints/{identifier}', tags=['Checkpoints'])
async def delete_checkpoint(identifier: str) -> dict:
    """
    Delete an  checkpoint by identifier.
    Returns a status dict.
    """
    async with get_async_session() as session:
        statement = select(Checkpoint).where(Checkpoint.identifier == identifier)
        result = await session.execute(statement)
        cp = result.scalars().one_or_none()
        if not cp:
            raise HTTPException(status_code=404, detail='checkpoint not found')
        await session.delete(cp)
        await session.commit()
        return {
            'status': 'success',
            'message': f'Checkpoint for identifier {identifier} deleted',
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


# Category endpoints
@app.post('/categories', tags=['Categories'], response_model=CategoryResponse)
async def create_category(payload: CategoryRequest) -> CategoryResponse:
    """
    Create a new category.
    """
    async with get_async_session() as session:
        cat = Category(**payload.model_dump())
        session.add(cat)
        await session.commit()
        await session.refresh(cat)
        return CategoryResponse.model_validate(cat)


@app.get('/categories', tags=['Categories'], response_model=list[CategoryResponse])
async def get_categories() -> list[CategoryResponse]:
    """
    Get all categories.
    Returns:
        List of all categories
    """
    async with get_async_session() as session:
        statement = select(Category)
        result = await session.execute(statement)
        categories = result.scalars().all()
        return [CategoryResponse.model_validate(c) for c in categories]


@app.get('/categories/{category_id}', tags=['Categories'], response_model=CategoryResponse)
async def get_category_by_id(category_id: int) -> CategoryResponse:
    """
    Get a category by ID.
    Args:
        category_id: ID of the category to retrieve
    Returns:
        Category data
    """
    async with get_async_session() as session:
        statement = select(Category).where(Category.category_id == category_id)
        result = await session.execute(statement)
        cat = result.scalars().one_or_none()
        if not cat:
            raise HTTPException(status_code=404, detail='Category not found')
        return CategoryResponse.model_validate(cat)


@app.get('/categories/name/{category_name}', tags=['Categories'], response_model=CategoryResponse)
async def get_category_by_name(category_name: str) -> CategoryResponse:
    """
    Get a category by name.
    Args:
        category_name: Name of the category to retrieve
    Returns:
        Category data
    """
    async with get_async_session() as session:
        statement = select(Category).where(Category.category_name == category_name)
        result = await session.execute(statement)
        cat = result.scalars().one_or_none()
        if not cat:
            raise HTTPException(status_code=404, detail='Category not found')
        return CategoryResponse.model_validate(cat)


@app.put('/categories/{category_id}', tags=['Categories'], response_model=CategoryResponse)
async def update_category(
    category_id: int, payload: CategoryRequest
) -> CategoryResponse:
    """
    Update a category.
    Args:
        category_id: ID of the category to update
        payload: Updated category data
    Returns:
        Updated category data
    """
    async with get_async_session() as session:
        statement = select(Category).where(Category.category_id == category_id)
        result = await session.execute(statement)
        cat = result.scalars().one_or_none()
        if not cat:
            raise HTTPException(status_code=404, detail='Category not found')

        for key, value in payload.model_dump().items():
            if hasattr(cat, key):
                setattr(cat, key, value)

        await session.commit()
        await session.refresh(cat)
        return CategoryResponse.model_validate(cat)


@app.delete('/categories/{category_id}', tags=['Categories'])
async def delete_category(category_id: int) -> dict:
    """
    Delete a category.
    Args:
        category_id: ID of the category to delete
    Returns:
        Deletion status
    """
    async with get_async_session() as session:
        statement = select(Category).where(Category.category_id == category_id)
        result = await session.execute(statement)
        cat = result.scalars().one_or_none()
        if not cat:
            raise HTTPException(status_code=404, detail='Category not found')

        await session.delete(cat)
        await session.commit()
        return {'status': 'success', 'message': 'Category deleted'}


# Merchant endpoints
@app.post('/merchants', tags=['Merchants'], response_model=MerchantResponse)
async def create_merchant(payload: MerchantRequest) -> MerchantResponse:
    """
    Create a new merchant.
    """
    async with get_async_session() as session:
        merch = Merchant(**payload.model_dump())
        session.add(merch)
        await session.commit()
        await session.refresh(merch)
        return MerchantResponse.model_validate(merch)


@app.get('/merchants', tags=['Merchants'], response_model=list[MerchantResponse])
async def get_merchants() -> list[MerchantResponse]:
    """
    Get all merchants.
    Returns:
        List of all merchants
    """
    async with get_async_session() as session:
        statement = select(Merchant)
        result = await session.execute(statement)
        merchants = result.scalars().all()
        return [MerchantResponse.model_validate(c) for c in merchants]


@app.get('/merchants/{merchant_id}', tags=['Merchants'], response_model=MerchantResponse)
async def get_merchant_by_id(merchant_id: int) -> MerchantResponse:
    """
    Get a merchant by ID.
    Args:
        merchant_id: ID of the merchant to retrieve
    Returns:
        Merchant data
    """
    async with get_async_session() as session:
        statement = select(Merchant).where(Merchant.merchant_id == merchant_id)
        result = await session.execute(statement)
        merch = result.scalars().one_or_none()
        if not merch:
            raise HTTPException(status_code=404, detail='Merchant not found')
        return MerchantResponse.model_validate(merch)


@app.get('/merchants/name/{merchant_name}', tags=['Merchants'], response_model=MerchantResponse)
async def get_merchant_by_name(merchant_name: str) -> MerchantResponse:
    """
    Get a merchant by name.
    Args:
        merchant_name: Name of the merchant to retrieve
    Returns:
        Merchant data
    """
    async with get_async_session() as session:
        statement = select(Merchant).where(Merchant.merchant_name == merchant_name)
        result = await session.execute(statement)
        merch = result.scalars().one_or_none()
        if not merch:
            raise HTTPException(status_code=404, detail='Merchant not found')
        return MerchantResponse.model_validate(merch)


@app.put('/merchants/{merchant_id}', tags=['Merchants'], response_model=MerchantResponse)
async def update_merchant(
    merchant_id: int, payload: MerchantRequest
) -> MerchantResponse:
    """
    Update a merchant.
    Args:
        merchant_id: ID of the merchant to update
        payload: Updated merchant data
    Returns:
        Updated merchant data
    """
    async with get_async_session() as session:
        statement = select(Merchant).where(Merchant.merchant_id == merchant_id)
        result = await session.execute(statement)
        merch = result.scalars().one_or_none()
        if not merch:
            raise HTTPException(status_code=404, detail='Merchant not found')

        for key, value in payload.model_dump().items():
            if hasattr(merch, key):
                setattr(merch, key, value)

        await session.commit()
        await session.refresh(merch)
        return MerchantResponse.model_validate(merch)


@app.delete('/merchants/{merchant_id}', tags=['Merchants'])
async def delete_merchant(merchant_id: int) -> dict:
    """
    Delete a merchant.
    Args:
        merchant_id: ID of the merchant to delete
    Returns:
        Deletion status
    """
    async with get_async_session() as session:
        statement = select(Merchant).where(Merchant.merchant_id == merchant_id)
        result = await session.execute(statement)
        merch = result.scalars().one_or_none()
        if not merch:
            raise HTTPException(status_code=404, detail='Merchant not found')

        await session.delete(merch)
        await session.commit()
        return {'status': 'success', 'message': 'Merchant deleted'}


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000, reload=True)
