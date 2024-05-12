import json
import boto3


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('awstip-infosectable')  # Replace with your table name


def lambda_handler(event, context):
    photo_id = event['photoId']
    email = event['email']
    photo_edit_path = event.get('photoEditPath', '')  # Handle optional attribute
    photo_path = event.get('photoPath', '')  
    status = event.get('status', 'pending')  # Set a default status


    item = {
        'PhotoId': photo_id,
        'Email': email,
        'PhotoEditPath': photo_edit_path,
        'PhotoPath': photo_path,
        'Status': status
    }


    table.put_item(Item=item)


    return {
        'statusCode': 200,
        'body': json.dumps('Photo added successfully')
    }
