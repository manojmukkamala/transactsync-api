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
    "account_owner": "Alice",
    "load_by": "agent"
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


## checkpoints

### GET
Get all checkpoints:

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/checkpoints" -H "accept: application/json" | jq
# Example response:
# {"checkpoints":[{"id":1,"identifier":"INBOX","checkpoint":"12345"},...]}
```

Get the last seen UID for a specific folder `INBOX` (returns null if not found):

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/checkpoints/INBOX" -H "accept: application/json" | jq
# Example response when exists:
# {"id":1,"identifier":"INBOX","checkpoint":"12345"}
# Example response when not found:
# {"id":null,"identifier":"INBOX","checkpoint":null}
```

### PUT
Set/update the last seen UID for folder `INBOX`:

```sh
curl -H "x-api-key: super-secret" -X PUT "http://127.0.0.1:8000/checkpoints/INBOX" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"checkpoint": "66666"}' | jq
# Example response:
# {"id":1,"identifier":"INBOX","checkpoint":12345}
```

### POST
Create a new email checkpoint:

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/checkpoints" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "INBOX",
    "checkpoint": "55555"
  }'
# Example response:
# {"id":1,"identifier":"INBOX","checkpoint":"55555"}
```

### DELETE
Delete the checkpoint for a folder:

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/checkpoints/INBOX" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Checkpoint for identifier INBOX deleted"}
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

### GET (filtered)

Filter transactions by date range and/or cycle_id:

```sh
# Get transactions between two dates
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/transactions?start_date=2026-02-12&end_date=2026-02-13" -H "accept: application/json" | jq

# Get transactions for a specific cycle
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/transactions?cycle_id=1" -H "accept: application/json" | jq

# Get transactions between two dates for a specific cycle
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/transactions?start_date=2026-01-01T00:00:00&end_date=2026-01-31T23:59:59&cycle_id=1" -H "accept: application/json" | jq
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
    "cycle_id": 1,
    "is_budgeted": 0,
    "is_deleted": 0
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
    "cycle_id": 1,
    "is_budgeted": 0,
    "is_deleted": 0    
  }' | jq
# Example response: same as GET but with updated fields
```

### DELETE

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/transactions/1" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Transaction deleted"}
```


## categories

### GET (all)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/categories" -H "accept: application/json" | jq
# Example response:
# [{"category_id":1,"category_name":"Food","category_description":"Groceries and dining","comments":null,"load_time":null,"load_by":null}]
```

### POST (create)

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/categories" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "category_name": "Entertainment",
    "category_description": "Movies, concerts, etc.",
    "comments": "For leisure activities"
  }' | jq
# Example response:
# {"category_id":2,"category_name":"Entertainment","category_description":"Movies, concerts, etc.","comments":"For leisure activities","load_time":null,"load_by":null}
```

### GET (by id)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/categories/1" -H "accept: application/json" | jq
# Example response:
# {"category_id":1,"category_name":"Food","category_description":"Groceries and dining","comments":null,"load_time":null,"load_by":null}
```

### GET (by name)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/categories/name/Entertainment" -H "accept: application/json" | jq
# Example response:
# {"category_id":2,"category_name":"Entertainment","category_description":"Movies, concerts, etc.","comments":"For leisure activities","load_time":null,"load_by":null}
```

### PUT

```sh
curl -H "x-api-key: super-secret" -X PUT "http://127.0.0.1:8000/categories/1" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "category_name": "Food",
    "category_description": "Groceries, dining and beverages",
    "comments": "Updated description"
  }' | jq
# Example response: same as GET but with updated fields
```

### DELETE

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/categories/1" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Category deleted"}
```

## merchants

### GET (all)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/merchants" -H "accept: application/json" | jq
# Example response:
# [{"merchant_id":1,"merchant_name":"Starbucks","merchant_description":"Coffee shop","comments":null,"load_time":null,"load_by":null}]
```

### POST (create)

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/merchants" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_name": "Amazon",
    "merchant_description": "Online retailer",
    "comments": "For shopping"
  }' | jq
# Example response:
# {"merchant_id":2,"merchant_name":"Amazon","merchant_description":"Online retailer","comments":"For shopping","load_time":null,"load_by":null}
```

### GET (by id)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/merchants/1" -H "accept: application/json" | jq
# Example response:
# {"merchant_id":1,"merchant_name":"Starbucks","merchant_description":"Coffee shop","comments":null,"load_time":null,"load_by":null}
```

### GET (by name)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/merchants/name/Amazon" -H "accept: application/json" | jq
# Example response:
# {"merchant_id":2,"merchant_name":"Amazon","merchant_description":"For shopping","comments":"Retail","load_time":null,"load_by":null}
```

### PUT

```sh
curl -H "x-api-key: super-secret" -X PUT "http://127.0.0.1:8000/merchants/1" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_name": "Starbucks",
    "merchant_description": "Coffee shop and bakery",
    "comments": "Updated description"
  }' | jq
# Example response: same as GET but with updated fields
```

### DELETE

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/merchants/1" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Merchant deleted"}
```


## emails

### GET (all)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/emails" -H "accept: application/json" | jq
# Example response:
# [{"email_id":1,"email_uid":12345,"folder":"INBOX","from_address":"sender@example.com","to_address":"recipient@example.com","email_date":"2026-01-15T10:30:00","load_time":null,"load_by":null}]
```

### POST (create)

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/emails" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email_uid": 54321,
    "folder": "INBOX",
    "from_address": "noreply@bank.com",
    "to_address": "user@example.com",
    "email_date": "2026-01-15T10:30:00"
  }' | jq
# Example response:
# {"email_id":2,"email_uid":54321,"folder":"INBOX","from_address":"noreply@bank.com","to_address":"user@example.com","email_date":"2026-01-15T10:30:00","load_time":null,"load_by":null}
```

### GET (by id)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/emails/1" -H "accept: application/json" | jq
# Example response:
# {"email_id":1,"email_uid":12345,"folder":"INBOX","from_address":"sender@example.com","to_address":"recipient@example.com","email_date":"2026-01-15T10:30:00","load_time":null,"load_by":null}
```

### GET (by uid)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/emails/uid/54321" -H "accept: application/json" | jq
# Example response:
# {"email_id":2,"email_uid":54321,"folder":"INBOX","from_address":"noreply@bank.com","to_address":"user@example.com","email_date":"2026-01-15T10:30:00","load_time":null,"load_by":null}
```

### GET (by folder)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/emails/folder/latest/INBOX" -H "accept: application/json" | jq
# Example response:
# {"email_id":2,"email_uid":54321,"folder":"INBOX","from_address":"noreply@bank.com","to_address":"user@example.com","email_date":"2026-01-15T10:30:00","load_time":null,"load_by":null}
```

### PUT

```sh
curl -H "x-api-key: super-secret" -X PUT "http://127.0.0.1:8000/emails/1" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "email_uid": 12345,
    "folder": "INBOX",
    "from_address": "sender@example.com",
    "to_address": "recipient@example.com",
    "email_date": "2026-01-15T10:30:00"
  }' | jq
# Example response: same as GET but with updated fields
```

### DELETE

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/emails/1" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Email deleted"}
```


## files

### GET (all)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/files" -H "accept: application/json" | jq
# Example response:
# [{"file_id":1,"file_name":"transaction_report_2026-01-15.csv","file_path":"/reports/2026/01","file_created_at":"2026-01-15T10:30:00","load_time":null,"load_by":null}]
```

### POST (create)

```sh
curl -H "x-api-key: super-secret" -X POST "http://127.0.0.1:8000/files" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "transaction_report_2026-01-15.csv",
    "file_path": "/reports/2026/01",
    "file_created_at": "2026-01-15T10:30:00"
  }' | jq
# Example response:
# {"file_id":2,"file_name":"transaction_report_2026-01-15.csv","file_path":"/reports/2026/01","file_created_at":"2026-01-15T10:30:00","load_time":null,"load_by":null}
```

### GET (by id)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/files/1" -H "accept: application/json" | jq
# Example response:
# {"file_id":1,"file_name":"transaction_report_2026-01-15.csv","file_path":"/reports/2026/01","file_created_at":"2026-01-15T10:30:00","load_time":null,"load_by":null}
```

### GET (by path)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/files/path//reports/2026/01" -H "accept: application/json" | jq
# Example response:
# [{"file_id":1,"file_name":"transaction_report_2026-01-15.csv","file_path":"/reports/2026/01","file_created_at":"2026-01-15T10:30:00","load_time":null,"load_by":null}]
```

### GET (latest by path)

```sh
curl -H "x-api-key: super-secret" -X GET "http://127.0.0.1:8000/files/path/latest//reports/2026/01" -H "accept: application/json" | jq
# Example response:
# {"file_id":1,"file_name":"transaction_report_2026-01-15.csv","file_path":"/reports/2026/01","file_created_at":"2026-01-15T10:30:00","load_time":null,"load_by":null}
```

### PUT

```sh
curl -H "x-api-key: super-secret" -X PUT "http://127.0.0.1:8000/files/1" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "transaction_report_2026-01-15.csv",
    "file_path": "/reports/2026/01",
    "file_created_at": "2026-01-15T10:30:00"
  }' | jq
# Example response: same as GET but with updated fields
```

### DELETE

```sh
curl -H "x-api-key: super-secret" -X DELETE "http://127.0.0.1:8000/files/1" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"File deleted"}
```