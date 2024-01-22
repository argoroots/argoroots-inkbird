import boto3
import json
from datetime import datetime, timedelta

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

    # Aggregate data by minute and calculate average Temperature and Humidity
    aggregated_data = {}
    for item in response['Items']:
        timestamp = datetime.strptime(item['Date'], '%Y-%m-%dT%H:%M:%S')
        key = timestamp.strftime('%Y-%m-%dT%H:00:00')

        if key not in aggregated_data:
            aggregated_data[key] = {'Temperature': [], 'Humidity': []}

        aggregated_data[key]['Temperature'].append(float(item['Temperature']))
        aggregated_data[key]['Humidity'].append(float(item['Humidity']))

    # Format the aggregated data
    data = [['Date', 'Temperature', 'Humidity']]
    for key, values in aggregated_data.items():
        data.append([
            key,
            round(sum(values['Temperature']) / len(values['Temperature']), 1),
            round(sum(values['Humidity']) / len(values['Humidity']), 1)
        ])

    # Convert data to JSON
    response_json = json.dumps(data)

    return {
        'statusCode': 200,
        'body': response_json
    }
