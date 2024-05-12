import json
import boto3
from PIL import Image


s3_client = boto3.client('s3')
ses_client = boto3.client('ses')
dynamodb = boto3.client('dynamodb')


def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    parts = key.split('/')
    filename = parts[1]
    photo_id = filename.split('_')[1].split('.')[0]


    try:
        with open('/tmp/original.png', 'wb') as f:
                s3_client.download_fileobj(bucket, key, f)
        with open('/tmp/template.png', 'wb') as f:
            s3_client.download_fileobj(bucket, "backgrounds/INFOSEC.png", f)


        # Load images
        original_img = Image.open('/tmp/original.png')
        template_img = Image.open('/tmp/template.png')


        # Resize template if needed
        template_img = template_img.resize(original_img.size)


        # Create a mask from the template (assuming the background is white)
        mask = template_img.convert('L').point(lambda p: 0 if p == 255 else 255)


        # Combine with the template
        original_img.paste(template_img, (0, 0), mask)
        print("Original Dimensions:", original_img.size)


        # Save edited image
        original_img.save('/tmp/edited.png')


        # Upload edited image to S3
        edited_image_key = f'edited-pic/edited_{photo_id}.png'
        s3_client.put_object(Body=open('/tmp/edited.png', 'rb'), Bucket=bucket, Key=edited_image_key)
       
        dynamodb.update_item(
            TableName='awstip-infosectable',
            Key={'PhotoId': {'N': photo_id}},
            UpdateExpression="SET PhotoEditPath = :path",
            ExpressionAttributeValues={
                ':path': {'S': edited_image_key}  
            }
        )
        print(f"Successfully updated PhotoEditPath in DynamoDB")


        print(f"Successfully edited and uploaded: {edited_image_key}")


    except Exception as e:
        print(f"Error processing image: {e}")
        raise e  # Re-raise to log the error
