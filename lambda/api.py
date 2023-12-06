import boto3
import json

DYNAMODB_TABLE_NAME = 'inkbird'

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    # Extract query parameters from the event
    sensor = event['queryStringParameters'].get('sensor')
    start = event['queryStringParameters'].get('start')
    end = event['queryStringParameters'].get('end')

    # Check if required parameters are missing
    if not sensor or not start or not end:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'One or more required query parameters are missing'})
        }

    # Query the DynamoDB table with a date range filter
    response = table.query(
        KeyConditionExpression='#sensor = :sensor_value AND #date_time BETWEEN :start AND :end',
        ExpressionAttributeNames={
            '#sensor': 'Sensor',
            '#date_time': 'Date',
        },
        ExpressionAttributeValues={
            ':sensor_value': sensor,
            ':start': start,
            ':end': end,
        },
        ScanIndexForward=True
    )

    # Format the data
    data = [['Date', 'Temperature', 'Humidity']]
    for item in response['Items']:
        data.append([item['Date'], float(item['Temperature']), float(item['Humidity'])])

    # Convert data to JSON
    response_json = json.dumps(data)

    return {
        'statusCode': 200,
        'body': response_json
    }
