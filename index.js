const AWS = require('aws-sdk');

var simpleemailservice = new AWS.SES({
    region: 'us-east-1'
});

var ses = new AWS.SES({ region: "us-east-1" });

const timetolive = 900;



var DynamoDocClient = new AWS.DynamoDB.DocumentClient({
    region: 'us-east-1'
});

var dynamodb = new AWS.DynamoDB();

exports.handler = (event, context, callback) => {

    console.log(event.Records[0].Sns.Message);


    var message = JSON.parse(event.Records[0].Sns.Message);
    console.log(message);



    var parameter = {
        Item: {
            'id': event.Records[0].Sns.MessageId,
            'EMAIL_ADDRESS': message.email_address,
            'QUESTION_ID': message.question_id,
            'ANSWER_ID': message.answer_id,
            'ANSWER_TEXT': message.answer_text,
            'LINK': message.link
        },
        TableName: "csye6225"
    };


    //function to put into dynamo db
    function putIntoDynamo() {
        return new Promise(function (resolve, reject) {
            DynamoDocClient.put(parameter, function (err, data) {
                if (err) {
                    reject(new Error(err));
                } else {
                    resolve(data);
                }
            });
        });
    }

    ////////////////////////////////////////////////////////////////

    async function putDynamoAsync() {
        var inserter = await putIntoDynamo();
    }


    ///////////////////////////////////////////////////////////////

    //send email function
    function sendEmail() {

        var params = {
            Destination: {
                ToAddresses: [message.email_address]
            },
            Message: {
                Body: {

                    Html: {
                        //Data: links
                        Data: '<html><head>' +
                            '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />' +
                            '</head><body>' +
                            'Hello,' +
                            '<br><br>' +
                            'A user has performed actions on the question that you posted.' +
                            '<br><br>' +
                            'Please refer below for information of the same.' +
                            '<br>' +
                            '<br>' +
                            '<div>Email Address: </div>' +
                            '<div>' + message.email_address + '</div>' +
                            '<br>' +
                            '<div>Question ID: </div>' +
                            '<div>' + message.question_id + '</div>' +
                            '<br>' +
                            '<div> Answer ID: </div>' +
                            '<div>' + message.answer_id + '</div>' +
                            '<br>' +
                            '<div> Answer Text: </div>' +
                            '<div>' + message.answer_text + '</div>' +
                            '<br>' +
                            '<div> Link: </div>' +
                            '<div>' +
                            '<a href=\'' + message.link + '\'>' + message.link + '</a>' + '</div>' +
                            '<br><br>' +
                            'Regards' +
                            '<br><br>' +
                            'CSYE6225' +
                            '<br><br>' +
                            +'</body></html>'
                    }
                },

                Subject: { Data: "This is a notification message from WebApp" },
            },
            Source: "webapp@prod.paragshah.me",
        };


        return ses.sendEmail(params).promise()

    }


    /////////////////////////////////////////////////////////////

    //function to get from dynamo db
    function getFromDynamo() {

        var params = {
            ExpressionAttributeNames: {
                "#QID": "QUESTION_ID",
                "#EM": "EMAIL_ADDRESS",
                "#ANS": "ANSWER_TEXT",
                '#LNK': "LINK"
            },
            ExpressionAttributeValues: {
                ":QUESTION_ID": message.question_id,
                ":EMAIL_ADDRESS": message.email_address,
                ":ANSWER_TEXT": message.answer_text,
                ":LINK": message.link

            },
            FilterExpression: "#QID = :QUESTION_ID AND #EM = :EMAIL_ADDRESS AND #ANS = :ANSWER_TEXT AND #LNK = :LINK",
            ConsistentRead: true,
            TableName: "csye6225"
        };

        DynamoDocClient.scan(params, function (err, data) {
            if (err) console.log(err, err.stack); // an error occurred
            else {
                console.log(data.Count);
                console.log(data);
                console.log(message.link);
                if (data.Count == (0)) {
                    sendEmail();

                }
            }        // successful response
        });
    }

    //////////////////////////////////////////////////////////////

    async function getFromDynamoAsync() {
        var caller = await getFromDynamo();
    }

    ///////////////////////////////////////////////////////////////

    //check answer text and answer id for N/A

    function checkForDelete() {
        if (message.answer_text == "N/A" && message.answer_id == "N/A") {
            sendEmail();
            putDynamoAsync();
        }
        else {
            getFromDynamoAsync();
            putDynamoAsync();

        }
    }

    checkForDelete();



}