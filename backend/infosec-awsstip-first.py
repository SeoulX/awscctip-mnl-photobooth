import json
import boto3
import io


s3Client = boto3.client('s3')
ses_client = boto3.client('ses')
dynamodb = boto3.client('dynamodb')


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    parts = key.split('/')
    filename = parts[1]
    photo_id = filename.split('_')[1].split('.')[0]


    if not key.startswith('edited-pic/'):
        print('File not in uploads folder. Skipping')
        return


    # Verify it's an image
    if not key.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        print('Not an image file. Skipping.')
        return


    try:
        response = dynamodb.get_item(
            TableName='awstip-infosectable',
            Key={'PhotoId': {'N': photo_id}}
        )
        email_address = response['Item']['Email']['S']
    except Exception as e:
        print(f"Error retrieving email from DynamoDB: {e}")
        return  # Handle error appropriately


    product_image_url = f"https://{bucket}.s3.amazonaws.com/{key}"
    template_data_json = json.dumps({
        'productImageURL': product_image_url,
        'photo_id': photo_id,
    })


    # Send email using SES template
    response = ses_client.send_templated_email(
        Source='awslc.mnl@tip.edu.ph',
        Destination={
            'ToAddresses': [email_address]
        },
        Template='FinalEmailTemplateAWSCCTIPM1',
        TemplateData=template_data_json
    )
    print("Template Data:", template_data_json)


    print("SES Response:", response)
   
    print('Email sent!')
