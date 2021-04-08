import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
from boto3.dynamodb.conditions import Key

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


'''
def lambda_handler(event, context):

    print('Testing Lambda', event)
    message_id = event["Records"][0]["Sns"]["MessageId"]
    message = json.loads(event["Records"][0]["Sns"]["Message"])

    dynamodb = boto3.resource("dynamodb")

    table = dynamodb.Table(DYNANODB_TABLE)
    resp = table.query(KeyConditionExpression=Key("id").eq(message_id))
    if resp["Count"] != 0:
        return {"statusCode": 400, "body": json.dumps("Message has already been sent.")}

    if message["on"] == "question_answered":
        subj = "A New Answer Posted to Your Question"
        cont = f"""
        Your question:
            - id: {message['question_id']}
            - question_text: {message['question_text']}
            - question_url: {message['question_url']}
        
        A new answer:
            - id: {message['answer_id']}
            - answer_text: {message['answer_text']}
            - answer_url: {message['answer_url']}
        """
    elif message["on"] == "answer_deleted":
        subj = "An Answer Deleted from Your Question"
        cont = f"""
        Your question:
            - id: {message['question_id']}
            - question_text: {message['question_text']}
            - question_url: {message['question_url']}
        
        The deleted answer:
            - id: {message['answer_id']}
            - answer_text: {message['answer_text']}
        """
    print("--->")
    _send_email(
        "webapp <notifications@paragshah.me>",
        message["question_creator_email"],
        subj,
        cont,
    )
    # for i in event:
    #     print(i)
    # TODO implement
    table.put_item(
        Item={
            "id": message_id,
            "on": message.get("on"),
            "question_id": message.get("question_id"),
            "question_creator_email": message.get("question_creator_email"),
            "question_url": message.get("question_url"),
            "answer_id": message.get("answer_id"),
            "answer_text": message.get("answer_text"),
            "answer_url": message.get("answer_url"),
        }
    )
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
    

    {'Records': [{'EventSource': 'aws:sns', 'EventVersion': '1.0', 'EventSubscriptionArn': 'arn:aws:sns:us-east-1:578033826244:sns_topic:35ffe68f-618a-438c-af33-2287701f6b00', 'Sns': {'Type': 'Notification', 'MessageId': '2badc683-5337-598d-88bc-9e6bf8c3b5f1', 'TopicArn': 'arn:aws:sns:us-east-1:578033826244:sns_topic', 'Subject': None, 'Message': 'Test message', 'Timestamp': '2021-04-08T06:59:00.999Z', 'SignatureVersion': '1', 'Signature': 'fy8/uoHSpiK8IpAkzVv8ZdfVkk6h9o05LCNfSQ6jettLlcZ4L1qrEm3c6f/HdYnfRE7Ta7XbypSWE4YpxFPZ9+RyRBKp6AGkhOkk/3+DPowNtRYuAnabaZrwfCcNdnI5GWiVxQ4xjqxKRfon7VhHXEb//e22uVxyaaoxMuMzWNEk2DcJhfeoj8BrExLiZKtZyDgYXxSbDW+0K99S8P3qwgRrcAmQiAwQLr26M1xt6KSMMwBbG/LSGvT8kwsEIAPfseMclOEf1oau9Vdq1/4Em0WP4iGcMvYdFMhQlj8CRiwFCINIzxb842Vanm1x0cAw0xH8SQKoBI6YCz7ietQdwA==', 'SigningCertUrl': 'https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem', 'UnsubscribeUrl': 'https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:578033826244:sns_topic:35ffe68f-618a-438c-af33-2287701f6b00', 'MessageAttributes': {}}}]}
'''

ses_client = boto3.client('ses')
db_resource = boto3.resource('dynamodb')
table = db_resource.Table('message_notification')


def lambda_handler(event, context):

    print('Testing Lambda', event)
    event = json.loads(event["Records"][0]['Sns']['Message'])
    recipient = event['recipient']
    message = event['message']
    print(recipient, message)

    status = get_record(message)
    print(status)
    if not status:
        print('testing if not status')
        ses_response = ses_client.send_email(
            Source='parag@paragshah.me',
            Destination={
                'ToAddresses': [
                    recipient
                ]
            },
            Message={
                'Subject': {
                    'Data': 'Your book has been changed'
                },
                'Body': {
                    'Text': {
                        'Data': message

                    }
                }
            }
        )
        insert_record(message)
        return "notify the user succesfully"
    else:
        return "duplicate message"


def insert_record(message_content):
    response = table.put_item(
        Item={
            "message": message_content
        }
    )
    return response["ResponseMetadata"]["HTTPStatusCode"]


def get_record(message_content):
    response = table.get_item(
        Key={
            "message": message_content
        }
    )
    if 'Item' in response:
        return "There is an item found "
    else:
        return ""
