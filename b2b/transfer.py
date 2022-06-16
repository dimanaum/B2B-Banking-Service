import json
import logging
import os
import time
from botocore.exceptions import ClientError
import boto3

dynamodb = boto3.resource('dynamodb')
dbclient = boto3.client('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def transfer(event, context):
    try:
        # parameter validation
        data = json.loads(event['body'])

        if 'amount' not in data:
            raise ValueError("Missing amount parameter: amount")

        if not isinstance(data['amount'], int) or int(data['amount']) <= 0:
            raise ValueError("The 'amount' parameter must be a positive integer.")

        if 'src_account_type' not in data:
            raise ValueError("Missing source account parameter: src_account_type")

        if 'dest_account' not in data:
            raise ValueError("Missing destination account parameter: dest_account")

        if 'dest_account_type' not in data:
            raise ValueError("Missing destination account parameter: dest_account_type")

        acc_id = event["requestContext"]["accountId"]
        amount = int(data['amount'])
        src_acc_type = data['src_account_type']
        dest_acc_id = data['dest_account']
        dest_acc_type = data['dest_account_type']

        if acc_id == dest_acc_id and src_acc_type == dest_acc_type:
            raise ValueError("Transferring to the same account is not permitted.")

        logger.info(("Calling Create(). Args: Account ID: {0}, Amount: {1}, Source Account Type: {2}," +
                     "Receiving Account ID: {3}, Receiving Account Type: {4},").format(
            acc_id, amount, src_acc_type, dest_acc_id, dest_acc_type
        ))

        # establishing a connection to the database
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

        # validate sender account
        query = table.get_item(Key={'id': acc_id, 'account_type': src_acc_type})
        if 'Item' not in query:
            raise ValueError("Sending user does not a " + src_acc_type + " account open.")

        # check balance
        sender_bal = int(query['Item']['balance'])
        if sender_bal < amount:
            raise ValueError("The transfer amount cannot exceed the balance on the account.")  # todo print bal

        # conditional timestamp collection for verification
        sender_rec_timestamp = query['Item']['updated_at']

        logger.info("Sending account verified.")

        # validate receiver account
        query = table.get_item(Key={'id': dest_acc_id, 'account_type': dest_acc_type})
        if 'Item' not in query:
            raise ValueError("Receiving user does not a " + dest_acc_type + " account open.")

        # conditional timestamp
        dest_rec_timestamp = query['Item']['updated_at']

        logger.info("Receiving account verified.")

        logger.info("Balances before transfer: Sender: {0}, Recipient: {1}".format(
            sender_bal, int(query['Item']['balance'])
        ))

        new_sender_bal = sender_bal - amount
        new_receiver_bal = int(query['Item']['balance']) + amount

        send_transaction(acc_id, new_sender_bal, src_acc_type, sender_rec_timestamp,
                         dest_acc_id, new_receiver_bal, dest_acc_type, dest_rec_timestamp)

        logger.info("Transfer complete.")
        # create a response
        response = {
            "statusCode": 200,
            "body": "Transfer complete."
        }

        return response

    except ClientError as e:
        logger.error(json.dumps(e.args))

        if e.response["Error"]["Code"] == 'ConditionalCheckFailedException':
            logger.error("Database record updated since validation read.")

            response = {
                "statusCode": 400,
                "body": "The record has been modified since its validation."
            }
            return response
        else:
            raise e

    except ValueError as e:
        logger.error(json.dumps(e.args))

        response = {
            "statusCode": 400,
            "body": json.dumps(e.args)
        }
        return response

    except Exception as e:
        logger.error(json.dumps(e.args))

        response = {
            "statusCode": 500,
            "body": json.dumps(e.args)
        }
        return response


def send_transaction(acc_id, new_sender_bal, src_acc_type, src_rec_timestamp,
                     dest_acct_id, new_dest_bal, dest_acct_type, dest_rec_timestamp):
    timestamp = int(time.time() * 1000)

    # build a DynamoDB transaction to update two records
    # Optimistic table locking is achieved via comparing the timestamp. If it is identical
    # to when it was read earlier, then the record has not been modified.
    table_name = os.environ['DYNAMODB_TABLE']
    response = dbclient.transact_write_items(
        TransactItems=[
            {
                'Update': {
                    "TableName": table_name,
                    'Key': {
                        'id': {"S": acc_id},
                        'account_type': {"S": src_acc_type}
                    },
                    "UpdateExpression": "SET balance = :balance, updated_at = :updated_at ",
                    "ConditionExpression": "updated_at = :rec_timestamp",
                    "ExpressionAttributeValues": {
                        ":balance": {"N": str(new_sender_bal)},
                        ":updated_at": {"N": str(timestamp)},
                        ":rec_timestamp": {"N": str(src_rec_timestamp)}
                    },
                    "ReturnValuesOnConditionCheckFailure": "ALL_OLD"
                }
            },
            {
                'Update': {
                    "TableName": table_name,
                    'Key': {
                        'id': {"S": dest_acct_id},
                        'account_type': {"S": dest_acct_type}
                    },
                    "UpdateExpression": "SET balance = :balance, updated_at = :updated_at ",
                    "ConditionExpression": "updated_at = :rec_timestamp",
                    "ExpressionAttributeValues": {
                        ":balance": {"N": str(new_dest_bal)},
                        ":updated_at": {"N": str(timestamp)},
                        ":rec_timestamp": {"N": str(dest_rec_timestamp)}
                    },
                    "ReturnValuesOnConditionCheckFailure": "ALL_OLD"
                }
            }
        ]
    )
