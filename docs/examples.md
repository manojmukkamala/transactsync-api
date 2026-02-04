```sh
curl -X 'PUT' 'http://127.0.0.1:8000/accounts/2' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"account_number": "22222222","financial_institution": "Test Bank","account_name": "Updated Test Account","account_owner": "Jane Doe"}'

curl -X 'DELETE' 'http://127.0.0.1:8000/accounts/3' -H 'accept: application/json'

curl -X 'GET' 'http://127.0.0.1:8000/accounts/1'  -H 'accept: application/json'  | jq 

curl -X 'PUT' \
  'http://127.0.0.1:8000/accounts/2' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "account_number": "999999999",
    "financial_institution": "Test Bank",
    "account_name": "Updated Test Account",
    "account_owner": "Jane Doe"
  }'
```