# Bank2Bank HTTP API

This is a serverless HTTP API developed as a solution for the coding assignment provided by Vendia. This uses a modified Serverless Framework template in combination with DynamoDB for data storage.

## Structure

This service has exactly one file for each function, e.g. `b2b/delete.py`. In each of these files, there is exactly one function defined. This does not include helper functions.

## Deploy

In order to deploy the endpoint, run

```bash
serverless
```

## Usage

You can create, get, list, delete, or transfer funds between accounts with the following commands:

### Create an account

```bash
curl -X POST https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b --data '{ "account_type": "Checking", "initial_balance": 1000 }' -H "Content-Type: application/json"
```
A return message will indicate whether the creation was successful or not. A user may only have up to 10 account types.

### List all accounts

```bash
curl https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b
```
A JSON list of all accounts associated with the caller user will be returned. If the user is an administrator, all accounts will be returned.

### Get one account

```bash
# Replace the <account_type> part with a real account type
curl https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b/<account_type>
```
If an associated account type exists for the user, it will be returned in JSON format.

### Transfer funds between accounts

```bash
# Replace the <id> part with a real id from your b2b table
curl -X PUT https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b --data '{"amount": 100, "src_account_type": "Checking", "dest_account": "XXXXXXXXXXXXX", "dest_account_type": "Savings"}' -H "Content-Type: application/json"
```
A return message will indicate whether the transfer was successful or not. For a transfer to be successful, the sender account must have sufficient funds.

### Delete an account

```bash
# Replace the <id> part with a real id from your b2b table
curl -X DELETE https://XXXXXXX.execute-api.us-east-1.amazonaws.com/b2b/<account_type>
```

A return message will indicate whether the deletion was successful or not. The account balance must be empty for it to be deleted.

