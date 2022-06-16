import os
import json
import logging
from b2b import decimalencoder
import boto3

dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get(event, context):
    try:
        # parameter validation
        if event['pathParameters']['account_type'] is None:
            raise ValueError("Missing account type parameter in URL")

        acc_type = event['pathParameters']['account_type']
        acc_id = event["requestContext"]["accountId"]

        logger.info("Calling Get(). Args: Account ID: {0}, Account type: {1}".format(acc_id, acc_type))

        # establishing a connection to the database
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

        query = table.get_item(Key={'id': acc_id, 'account_type': acc_type})
        if 'Item' not in query:
            raise ValueError("There is no " + acc_type + " account type associated with this user.")

        logger.info("Returning account details.")
        # create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(query['Item'], cls=decimalencoder.DecimalEncoder)
        }

        return response

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
