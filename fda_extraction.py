import json
import boto3
import requests
from datetime import datetime

def lambda_handler(event, context):
    # Step 1: Set API endpoint and parameters
    url = "https://api.fda.gov/drug/event.json"
    params = {
        "search": 'patient.drug.medicinalproduct:"paracetamol"',
        "limit": 100
    }

    try:
        # Step 2: Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Step 3: Generate a filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 🔶 CHANGE THIS LINE:
        file_name = f"paracetamol_raw_{timestamp}.json"

        # 🔶 AND THIS LINE:
        s3_key = f"raw_data/to_processed/{file_name}"

        # Step 4: Upload to S3
        s3 = boto3.client('s3')
        bucket_name = "fda-etl-project-sujal"

        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(data),
            ContentType='application/json'
        )

        return {
            "statusCode": 200,
            "body": f"Data successfully uploaded to S3 as {s3_key}"
        }

    except requests.exceptions.RequestException as e:
        return {
            "statusCode": 500,
            "body": f"API request failed: {e}"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {e}"
        }
