import json
import os
import logging
from b2b import decimalencoder
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
admin_ids = ["XXXXXXXXXXXXXX"]  # todo: move out of source code


def list(event, context):
    try:
        # parameter validation
        acc_id = event["requestContext"]["accountId"]

        logger.info("Calling List(). Args: Account ID: {0},".format(acc_id))

        # establishing a connection to the database
        table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

        # determining whether the user is an admin or not
        if acc_id in admin_ids:
            result = table.scan()
        else:
            result = table.scan(FilterExpression=Attr('id').eq(acc_id))

        output = json.dumps(result['Items'], cls=decimalencoder.DecimalEncoder)

        logger.info("Sending list of accounts.")
        # create a response
        response = {
            "statusCode": 200,
            "body": output
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
