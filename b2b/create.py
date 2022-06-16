import json
import logging
import os
import time
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
dbclient = boto3.client('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create(event, context):
    try:
        # parameter validation
        data = json.loads(event['body'])

        if 'account_type' not in data:
            raise ValueError("Missing account type parameter: account_type")

        if 'initial_balance' not in data:
            raise ValueError("Missing balance parameter: initial_balance")

        if not isinstance(data['initial_balance'], int) or int(data['initial_balance']) < 0:
            raise ValueError("Balance must be a valid integer greater than or equal to 0.")

        acc_id = event["requestContext"]["accountId"]
        acc_type = data['account_type']
        init_bal = int(data['initial_balance'])

        logger.info("Calling Create(). Args: Account ID: {0}, Account type: {1}, Initial Balance: {2}".format(
            acc_id, acc_type, init_bal
        ))

        # database connection
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

        # verify that amount limit has not been reached
        result = table.scan(FilterExpression=Attr('id').eq(acc_id))
        if len(result['Items']) >= 10:
            raise ValueError("User may not have more than 10 accounts open.")

        timestamp = int(time.time() * 1000)

        logger.info("Time of account creation: " + str(datetime.fromtimestamp(time.time())))

        item = {
            'id': acc_id,
            'account_type': acc_type,
            'balance': init_bal,
            'updated_at': timestamp
        }

        # write the record to the database
        table.put_item(Item=item, ConditionExpression=Attr("id").ne(acc_id) & Attr("account_type").ne(acc_type))

        logger.info("Record successfully created.")

        # create a response
        response = {
            "statusCode": 200,
            "body": "Record created successfully."
        }
        return response

    except ClientError as e:
        logger.error(json.dumps(e.args))

        if e.response["Error"]["Code"] == 'ConditionalCheckFailedException':
            logger.error("Account type already exists for this user.")
            response = {
                "statusCode": 400,
                "body": "Account type already exists for this user."
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
