import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from boto3.dynamodb.conditions import Key

# SMTP credentials for domain paragshah.me
SMTP_SERVER = "email-smtp.us-east-1.amazonaws.com"
SMTP_PORT = 587
SMTP_UNAME = "AKIAZCR4ENDJGT2HJ3FX"
SMTP_PWD = "BCOI1DQobSPExP0Z0FEZdgGlaCpOayWUPcvGqrD59oub"
DYNANODB_TABLE = os.environ["DYNANODB_TABLE"]


def _send_email(fro, to, subject, content, html=False):
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_UNAME, SMTP_PWD)

        msg = MIMEMultipart()
        msg["From"] = fro
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(content + "\n\n\n")) if not html else msg.attach(
            MIMEText(content + "<br><br><br>", "html")
        )

        server.sendmail(fro, to, str(msg))


def lambda_handler(event, context):

    db_resource = boto3.resource('dynamodb')
    table = db_resource.Table(DYNANODB_TABLE)
    print('Table - ', table)

    print('Testing Lambda', event)
    message_id = event["Records"][0]["Sns"]["MessageId"]
    event = json.loads(event["Records"][0]['Sns']['Message'])
    user_email = event['user_email']
    message = event['message']
    print(user_email, message)

    
    resp = table.query(KeyConditionExpression=Key("id").eq(message_id))
    print(resp["Count"], resp)
    if resp["Count"] != 0:
        print('if test')
        return {"statusCode": 400, "body": json.dumps("Message has already been sent.")}

    if 'created' in message:
        ''' You created a book '''

        print('Book created email test')
        subj = 'Your book has been created'

        _send_email(
            "parag@paragshah.me",
            user_email,
            subj,
            message,
        )

        table.put_item(
            Item={
                "id": message_id,
                "message": message
            }
        )

        return {"statusCode": 200, "body": json.dumps("Hello from Lambda! Notification sent for book creation")}

    elif 'deleted' in message:
        ''' You deleted a book '''

        print('Book deleted email test')
        subj = 'Your book has been deleted'

        _send_email(
            "parag@paragshah.me",
            user_email,
            subj,
            message,
        )

        return {"statusCode": 200, "body": json.dumps("Hello from Lambda! Notification sent for book deletion")}
