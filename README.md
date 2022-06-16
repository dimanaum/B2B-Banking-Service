# Bank2Bank HTTP API

This is a serverless HTTP API developed as a solution for the coding assignment provided by Vendia. This uses a modified Serverless Framework template.

## Structure

This service has a separate directory for all the b2b operations. For each operation exactly one file exists e.g. `b2b/delete.py`. In each of these files there is exactly one function defined.

## Deploy

In order to deploy the endpoint simply run

```bash
serverless deploy
```

## Usage

You can create, get, list, delete, or transfer funds between accounts with the following commands:

### Create an account

```bash
curl -X POST https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b --data '{ "account_type": "Checking", "Initial Balance": "1000" }' -H "Content-Type: application/json"
```

### List all accounts

```bash
curl https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b
```

### Get one account

```bash
# Replace the <account_type> part with a real account type
curl https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b/<account_type>
```

### Transfer funds between accounts

```bash
# Replace the <id> part with a real id from your b2b table
curl -X PUT https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b --data '{"amount": 100, "src_account_type": "Checking", "dest_account": "XXXXXXXXXXXXX", "dest_account_type": "Savings"}' -H "Content-Type: application/json"
```

### Delete an account

```bash
# Replace the <id> part with a real id from your b2b table
curl -X DELETE https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b/<account_type>
```

The account balance must be empty for it to be deleted.

