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
    

    Testing Lambda {'Records': [{'EventSource': 'aws:sns', 'EventVersion': '1.0', 'EventSubscriptionArn': 'arn:aws:sns:us-east-1:578033826244:sns_topic:35ffe68f-618a-438c-af33-2287701f6b00', 'Sns': {'Type': 'Notification', 'MessageId': '9d1c95c1-9f03-5534-a445-cd295871b69c', 'TopicArn': 'arn:aws:sns:us-east-1:578033826244:sns_topic', 'Subject': None, 'Message': '{"user_email": "paragshah367@gmail.com", "message": "You created a book. Book id: 66e678a6-bef2-4380-a5bb-8fa3a7258770\\n Book link: prod.paragshah.me/book/66e678a6-bef2-4380-a5bb-8fa3a7258770"}', 'Timestamp': '2021-04-08T08:56:18.349Z', 'SignatureVersion': '1', 'Signature': 'JXe9Mgym0A43AMmCm2jLiFL7aQRlUc4vON6YeuJ8sWwjq6w2Pj3GGFEwq+bGHwEqQ+otpY+IXcK+mt2n/Elr3QfPG3I/z0OELKPbVdTYPgxCuGJni2Dy1HifqUn5gf/xTH3Gk3/VV10o81PrQiNOwN2eROw2HDW7Z3exSapj1Sc8kG+tHWfKMRPE5KFnYG5N4hmD0RakMg4L+UT6i/eWDFFHSSIAKzdGdgyGKZ+zEkt8OfjvyYauZY3WL8n/wOyF0TBBIfA3BctTX5M0OMW+fZe36RALdZKTkRiKYLWMMx+m07PheZNf8JUPPJiGFlN2qjQn5CELpEOzw06R5MApOw==', 'SigningCertUrl': 'https://sns.us-east-1.amazonaws.com/SimpleNotificationService-010a507c1833636cd94bdb98bd93083a.pem', 'UnsubscribeUrl': 'https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:578033826244:sns_topic:35ffe68f-618a-438c-af33-2287701f6b00', 'MessageAttributes': {}}}]}


'''

ses_client = boto3.client('ses')
db_resource = boto3.resource('dynamodb')
# table = db_resource.Table('message_notification')
table = db_resource.Table(DYNANODB_TABLE)


def lambda_handler(event, context):

    ses_client = boto3.client('ses')
    db_resource = boto3.resource('dynamodb')
    # table = db_resource.Table('message_notification')
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
        ses_response = ses_client.send_email(
            Source='parag@paragshah.me',
            Destination={
                'ToAddresses': [
                    user_email
                ]
            },
            Message={
                'Subject': {
                    'Data': 'Your book has been created'
                },
                'Body': {
                    'Text': {
                        'Data': message

                    }
                }
            }
        )
        insert_record(message)
        return "notify the user successfully"

    elif 'deleted' in message:
        ''' You deleted a book '''
        print('elif test')

    # status = get_record(message)
    # print(status)
    # if not status:
    #     print('testing if not status')
    #     ses_response = ses_client.send_email(
    #         Source='parag@paragshah.me',
    #         Destination={
    #             'ToAddresses': [
    #                 user_email
    #             ]
    #         },
    #         Message={
    #             'Subject': {
    #                 'Data': 'Your book has been changed'
    #             },
    #             'Body': {
    #                 'Text': {
    #                     'Data': message

    #                 }
    #             }
    #         }
    #     )
    #     insert_record(message)
    #     return "notify the user successfully"

    # else:
    #     return "duplicate message"


def insert_record(message_content):
    response = table.put_item(
        Item={
            "message": message_content
        }
    )
    return response["ResponseMetadata"]["HTTPStatusCode"]


def get_record(message_content):
    try:
        response = table.get_item(
            Key={
                "message": message_content
            }
        )
    except:
        if 'Item' in response:
            return "There is an item found "
        else:
            return ""
