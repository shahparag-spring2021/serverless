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