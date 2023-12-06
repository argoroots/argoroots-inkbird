import boto3
import csv
import email

from datetime import datetime
from email.policy import default

# Initialize the AWS clients
dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
ses = boto3.client('ses')

# Specify your S3 bucket and DynamoDB table name
S3_BUCKET_NAME = 'inkbird'
DYNAMODB_TABLE_NAME = 'inkbird'
SENSORS = ['Garage', 'Storage']
TO_EMAIL = 'argo@roots.ee'
FROM_EMAIL = 'argo@roots.ee'

def lambda_handler(event):
    for record in event['Records']:
        # Get the S3 bucket and object key
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Download the email attachment from S3
        email_data = s3.get_object(Bucket=bucket, Key=key)['Body'].read()

        # Parse the email
        msg = email.message_from_bytes(email_data, policy=default)

        # Extract the sender's email address
        sender = msg['from']

        # Process the email attachment
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue

            filename = part.get_filename()

            if filename:
                sensor = filename.split('_')[0]

                if sensor in SENSORS:
                    print(f'CSV: {filename}')
                    rows = process_email_attachment(part, sensor)

                    # Send a confirmation email
                    send_email(
                        subject='Inkbird Data Received',
                        body=f'Inkbird file {filename} received from {sender}.\n\n{rows} rows added.',
                    )
                else:
                    print(f'Unknown sensor: {sensor}')

                    # Send a warning email
                    send_email(
                        subject='Inkbird Data Received - Unknown Sensor',
                        body=f'Inkbird file {filename} received from {sender}.\n\nUnknown sensor "{sensor}"!',
                    )


def process_email_attachment(attachment, sensor):
    csv_data = attachment.get_payload(decode=True).decode().splitlines()
    rows = 0

    # Parse the CSV file and add data to DynamoDB
    for row in csv.reader(csv_data):
        try:
            date = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
            temperature = float(row[1])
            humidity = float(row[2])

            add_data_to_dynamodb(sensor, date, temperature, humidity)

            rows += 1
        except:
            print(row)

    print(f'Rows: {rows}')

    return rows


def add_data_to_dynamodb(sensor, date, temperature, humidity):
    # Add data to DynamoDB table
    try:
        response = dynamodb.put_item(
            TableName=DYNAMODB_TABLE_NAME,
            Item={
                'Sensor': {'S': sensor},
                'Date': {'S': date.isoformat(sep='T', timespec='auto')},
                'Temperature': {'S': str(temperature) },
                'Humidity': {'S': str(humidity) }
            }
        )

        return response
    except Exception as e:
        print(e)

        return False


def send_email(subject, body):
    try:
        response = ses.send_email(
            Source = FROM_EMAIL,
            Destination = {
                'ToAddresses': [TO_EMAIL],
            },
            Message = {
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    'Text': {
                        'Data': body,
                    },
                },
            },
        )
    except Exception as e:
        print(e)
