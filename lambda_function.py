import json
from PIL import Image, ImageDraw
from io import BytesIO
import base64
import boto3

bucket_name = "imagemasks"

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    print(event)
    http_body = json.loads(event['body'])

    uuid = http_body["uuid"]

    x_arrays = http_body["x_array"]
    y_arrays = http_body["y_array"]

    width = http_body["size"]["width"]
    height = http_body["size"]["height"]

    mask_key = f"mask/{uuid}.png"
    upload_mask(s3_client,mask_key,x_arrays, y_arrays, width, height)
    
    url = presigned_url(s3_client,mask_key)

    response = {
        "statusCode": 200,
        "body": {
            "url" : url
        }
    }

    return response

def upload_mask(s3_client,mask_key, x_arrays, y_arrays, width, height):
    # Create a blank image with black background
    image = Image.new("RGB", (width, height), "black")
    # Create a Draw object
    draw = ImageDraw.Draw(image)
    for i in range(len(x_arrays)): # total number of shapes
        x_array = x_arrays[i]
        y_array = y_arrays[i]
        example_coordinates = []
        for j in range(len(x_array)):
            example_coordinates.append((x_array[j] * width, y_array[j] * height))
            # Draw and fill the shape with white
        draw.polygon(example_coordinates, fill="white", outline=None)

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)
    
    s3_client.put_object(
        Body=buffered, 
        Bucket=bucket_name, 
        Key=mask_key,
        ContentType='image/png')

def presigned_url(s3_client,key):
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket_name,
            'Key': key,
            'ResponseContentType': 'image/png'
        },
        ExpiresIn=3600 # one hour in seconds, increase if needed
    )

    return url

