# Examples

## accounts

### GET

```sh
curl -X 'GET' 'http://127.0.0.1:8000/accounts/1'  -H 'accept: application/json'  | jq 
```

### PUT
```sh
curl -X 'PUT' 'http://127.0.0.1:8000/accounts/1' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"account_number": "22222222","financial_institution": "Test Bank","account_name": "Updated Test Account","account_owner": "Jane Doe"}'

curl -X 'PUT' \
  'http://127.0.0.1:8000/accounts/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "account_number": "999999999",
    "financial_institution": "Test Bank",
    "account_name": "Updated Test Account",
    "account_owner": "Jane Doe"
  }'
```

### POST
Create a new account:

```sh
curl -X POST "http://127.0.0.1:8000/accounts" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "account_number": "12345678",
    "financial_institution": "Example Bank",
    "account_name": "My Checking",
    "account_owner": "Alice"
  }'
# Example response (created account):
# {"account_id": 5, "account_number": "12345678", "financial_institution": "Example Bank", "account_name": "My Checking", "account_owner": "Alice", "active": true, "comments": null, "load_time": null, "load_by": null}
```

### DELTE
```sh
curl -X 'DELETE' 'http://127.0.0.1:8000/accounts/1' -H 'accept: application/json'

````

## email_checkpoints

### GET
Get all email checkpoints:

```sh
curl -X GET "http://127.0.0.1:8000/email_checkpoints" -H "accept: application/json" | jq
# Example response:
# {"checkpoints":[{"id":1,"folder":"INBOX","last_seen_uid":12345},...]}
```

Get the last seen UID for a specific folder `INBOX` (returns null if not found):

```sh
curl -X GET "http://127.0.0.1:8000/email_checkpoints/INBOX" -H "accept: application/json" | jq
# Example response when exists:
# {"id":1,"folder":"INBOX","last_seen_uid":12345}
# Example response when not found:
# {"id":null,"folder":"INBOX","last_seen_uid":null}
```

### PUT
Set/update the last seen UID for folder `INBOX`:

```sh
curl -X PUT "http://127.0.0.1:8000/email_checkpoints/INBOX" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"last_seen_uid": 12345}' | jq
# Example response:
# {"id":1,"folder":"INBOX","last_seen_uid":12345}
```

### POST
Create a new email checkpoint:

```sh
curl -X POST "http://127.0.0.1:8000/email_checkpoints" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "folder": "INBOX",
    "last_seen_uid": 55555
  }' | jq
# Example response:
# {"id":2,"folder":"INBOX","last_seen_uid":55555}
```

### DELETE
Delete the checkpoint for a folder:

```sh
curl -X DELETE "http://127.0.0.1:8000/email_checkpoints/INBOX" -H "accept: application/json" | jq
# Example response:
# {"status":"success","message":"Checkpoint for folder INBOX deleted"}
```