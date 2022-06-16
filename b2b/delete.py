import json
import logging
import os
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def delete(event, context):
    try:
        # parameter validation
        if event['pathParameters']['account_type'] is None:
            raise ValueError("Missing account type parameter: account_type")

        acc_type = event['pathParameters']['account_type']
        acc_id = event["requestContext"]["accountId"]

        logger.info("Calling Delete(). Args: Account ID: {0}, Account type: {1}".format(acc_id, acc_type))

        # establishing a connection to the database
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

        query = table.get_item(Key={'id': acc_id, 'account_type': acc_type})
        if 'Item' not in query:
            raise ValueError("There is no " + acc_type + " account type associated with this user.")

        # check balance
        if int(query['Item']['balance']) > 0:
            raise ValueError("Balance must be empty for the account to be deleted.")

        # delete the record from the database
        table.delete_item(
            Key={
                'id': acc_id,
                'account_type': acc_type
            },
            ConditionExpression=Attr("id").exists() & Attr("account_type").exists()
        )

        logger.info("Account deleted successfully.")

        # create a response
        response = {
            "statusCode": 200,
            "body": "Account successfully removed."
        }
        return response

    except ClientError as e:
        logger.error(json.dumps(e.args))

        if e.response["Error"]["Code"] == 'ConditionalCheckFailedException':
            response = {
                "statusCode": 400,
                "body": "Record was modified since validation."
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
