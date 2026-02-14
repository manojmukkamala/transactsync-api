# Examples

## accounts

### GET

```sh
curl -H "x-api-key: super-secret" -X 'GET' 'http://127.0.0.1:8000/accounts/1'  -H 'accept: application/json'  | jq 
```

### GET by account number
Get account_id by account_number:

```sh
curl -H "x-api-key: super-secret" -X 'GET' 'http://127.0.0.1:8000/accounts/by-number?account_number=007'  -H 'accept: application/json'  | jq 
# Example response when account exists:
# {"account_id": 12}
# Example response when account doesn't exist:
# {"account_id": null}
```

### PUT
```sh
curl -H "x-api-key: super-secret" -X 'PUT' 'http://127.0.0.1:8000/accounts/1' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"account_number": "22222222","financial_institution": "Test Bank","account_name": "Updated Test Account","account_owner": "Jane Doe"}' | jq

curl -H "x-api-key: super-secret" -X 'PUT' \
  'http://127.0.0.1:8000/accounts/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "account_number": "999999999",
    "financial_institution": "Test Bank",
    "account_name": "Updated Test Account",
    "account_owner": "Jane Doe"
  }' | jq
```

### POST
Create a new account:

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/accounts" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "account_number": "12345678",
    "financial_institution": "Example Bank",
    "account_name": "My Checking",
    "account_owner": "Alice"
  }' | jq
# Example response (created account):
# {"account_id": 5, "account_number": "12345678", "financial_institution": "Example Bank", "account_name": "My Checking", "account_owner": "Alice", "active": true, "comments": null, "load_time": null, "load_by": null}
```

### DELETE
```sh
curl -H "x-api-key: super-secret" -X 'DELETE' 'http://127.0.0.1:8000/accounts/1' -H 'accept: application/json' | jq
```


## email_checkpoints

### GET
Get all email checkpoints:

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/email_checkpoints" -H "accept: application/json" | jq
# Example response:
# {"checkpoints":[{"id":1,"folder":"INBOX","last_seen_uid":12345},...]}
```

Get the last seen UID for a specific folder `INBOX` (returns null if not found):

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/email_checkpoints/INBOX" -H "accept: application/json" | jq
# Example response when exists:
# {"id":1,"folder":"INBOX","last_seen_uid":12345}
# Example response when not found:
# {"id":null,"folder":"INBOX","last_seen_uid":null}
```

### PUT
Set/update the last seen UID for folder `INBOX`:

```sh
curl -H "x-api-key: super-secret" -X PUT "http://127.0.0.1:8000/email_checkpoints/INBOX" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"last_seen_uid": 12345}' | jq
# Example response:
# {"id":1,"folder":"INBOX","last_seen_uid":12345}
```

### POST
Create a new email checkpoint:

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/email_checkpoints" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "folder": "INBOX",
    "last_seen_uid": 55555
  }'
# Example response:
# {"id":2,"folder":"INBOX","last_seen_uid":55555}
```

### DELETE
Delete the checkpoint for a folder:

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/email_checkpoints/INBOX" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Checkpoint for folder INBOX deleted"}
```


## cycles

### GET (all)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/cycles" -H "accept: application/json" | jq
# Example response:
# [{"cycle_id":1,"cycle_start":"2026-01-01T00:00:00","cycle_end":"2026-01-31T23:59:59","cycle_description":null,"comments":null,"created_at":null,"updated_at":null}]
```

### POST (create)

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/cycles" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "cycle_start": "2026-01-01T00:00:00",
    "cycle_end": "2026-01-31T23:59:59",
    "cycle_description": "January cycle",
    "comments": "Auto-created"
  }' | jq
# Example response:
# {"cycle_id":1,"cycle_start":"2026-01-01T00:00:00","cycle_end":"2026-01-31T23:59:59","cycle_description":"January cycle","comments":"Auto-created","created_at":null,"updated_at":null}
```

### GET (by id)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/cycles/1" -H "accept: application/json" | jq
# Example response:
# {"cycle_id":1,"cycle_start":"2026-01-01T00:00:00","cycle_end":"2026-01-31T23:59:59","cycle_description":"January cycle","comments":"Auto-created","created_at":null,"updated_at":null}
```

### PUT

```sh
curl -H "x-api-key: super-secret" -X PUT "http://127.0.0.1:8000/cycles/1" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "cycle_start": "2026-01-01T00:00:00",
    "cycle_end": "2026-01-31T23:59:59",
    "cycle_description": "January cycle - updated",
    "comments": "Updated"
  }' | jq
# Example response: same as GET but with updated fields
```

### DELETE

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/cycles/1" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Cycle deleted"}
```

### GET cycle id for a transaction date
Return the cycle that includes the given transaction date (query param `transaction_date`):

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/cycles/for-date?transaction_date=2026-01-15T12:00:00" -H "accept: application/json" | jq
# Example response when found:
# {"cycle_id":1}
# Example response when not found:
# {"cycle_id":null}
```


## transactions

### GET (all)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/transactions" -H "accept: application/json" | jq
# Example response:
# [{"transaction_id":1,"transaction_date":"2026-01-15T10:30:00","transaction_amount":150.0,"merchant":"Starbucks","account_id":1,"from_address":"noreply@starbucks.com","to_address":"user@example.com","email_uid":100,"email_date":"2026-01-15T10:30:00","transaction_type":"purchase","cycle_id":1,...}]
```

### POST (create)

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/transactions" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_date": "2026-01-15T10:30:00",
    "transaction_amount": 150.00,
    "merchant": "Starbucks",
    "account_id": 1,
    "from_address": "noreply@starbucks.com",
    "to_address": "user@example.com",
    "email_uid": 100,
    "email_date": "2026-01-15T10:30:00",
    "transaction_type": "purchase",
    "cycle_id": 1
  }' | jq
# Example response:
# {"transaction_id":1,"transaction_date":"2026-01-15T10:30:00","transaction_amount":150.0,"merchant":"Starbucks","account_id":1,"from_address":"noreply@starbucks.com","to_address":"user@example.com","email_uid":100,"email_date":"2026-01-15T10:30:00","transaction_type":"purchase","cycle_id":1,...}
```

### GET (by id)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/transactions/1" -H "accept: application/json" | jq
# Example response:
# {"transaction_id":1,"transaction_date":"2026-01-15T10:30:00","transaction_amount":150.0,"merchant":"Starbucks","account_id":1,"from_address":"noreply@starbucks.com","to_address":"user@example.com","email_uid":100,"email_date":"2026-01-15T10:30:00","transaction_type":"purchase","cycle_id":1,...}
```

### PUT

```sh
curl -H "x-api-key: super-secret" -X PUT "http://127.0.0.1:8000/transactions/1" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_date": "2026-01-15T10:30:00",
    "transaction_amount": 175.00,
    "merchant": "Starbucks",
    "account_id": 1,
    "from_address": "noreply@starbucks.com",
    "to_address": "user@example.com",
    "email_uid": 100,
    "email_date": "2026-01-15T10:30:00",
    "transaction_type": "purchase",
    "cycle_id": 1
  }' | jq
# Example response: same as GET but with updated fields
```

### DELETE

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/transactions/1" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Transaction deleted"}
```
