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
    

    {'Records': [{'EventSource': 'aws:sns', 'EventVersion': '1.0', 'EventSubscriptionArn': 'arn:aws:sns:us-east-1:578033826244:sns_topic:35ffe68f-618a-438c-af33-2287701f6b00', 'Sns': {'Type': 'Notification', 'MessageId': 'f311760d-2bb8-57dd-b3be-2ee5588200d3', 'TopicArn': 'arn:aws:sns:us-east-1:578033826244:sns_topic', 'Subject': None, 'Message': 'm1', 'Timestamp': '2021-04-08T02:56:58.948Z', 'SignatureVersion': '1', 'Signature': 'UQtKkoYpq+8wIgkRGo/XuamjWCmI6wy+4UUJ8FpI0Es/aK9uhpWb1yodjIIIUEZRlrxskRjq3NAx7xDf+psxu5IsFKaiZA2CzzrM8hdNa/mjKkJi5zPxLGaqK3X0CJ1D6rk7Ty5rbjqahy77HvMNMEbmQo/4jBKYH9sD5pBO8WW+VyTEbsO3jEGCNU+xS/8mcnACCBl6kATgWX04CEKaV5lsfl1yfXRb8pHSN6Ad1EdsJP49QD2epSo13qBu8rDvrhWi+sT02bOEo+eHNA7hswCtRrSkla45WCUBVM38tKtfCgSKLbvqpE6ErCoSylwPRHLkX/2oDVwy7gYyifyEFA==', 'SigningCertUrl': 'https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem', 'UnsubscribeUrl': 'https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:578033826244:sns_topic:35ffe68f-618a-438c-af33-2287701f6b00', 'MessageAttributes': {}}
    }
    ]}
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
        return " duplicate message"


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
