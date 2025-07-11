import json
import boto3
import pandas as pd
from io import StringIO
from datetime import datetime

# Setup AWS S3 clients
s3 = boto3.client('s3')
s3_resource = boto3.resource('s3')

# S3 bucket and folder names
bucket_name = "fda-etl-project-sujal"
to_processed_folder = "raw_data/to_processed/"
processed_folder = "raw_data/processed_data/"
analytics_folder = "transformed_data/analytics_ready/"

def lambda_handler(event, context):
    # Step 1: List files in raw_data/to_processed/
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=to_processed_folder)
    
    files = []
    for file in response.get('Contents', []):
        if file['Key'].endswith('.json'):
            files.append(file['Key'])

    # Step 2: Process each file one by one
    for file_key in files:
        file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_data = file_obj['Body'].read()
        json_data = json.loads(file_data)

        # Extract 'results' section
        records = json_data['results']
        df = pd.DataFrame(records)

        # Step 3: Extract nested values into new columns
        df['source_qualification'] = df['primarysource'].apply(lambda x: x.get('qualification') if isinstance(x, dict) else None)
        df['sender_org'] = df['sender'].apply(lambda x: x.get('senderorganization') if isinstance(x, dict) else None)
        df['receiver_org'] = df['receiver'].apply(lambda x: x.get('receiverorganization') if isinstance(x, dict) else None)
        df['weight_kg'] = df['patient'].apply(lambda x: x.get('patientweight') if isinstance(x, dict) else None)
        df['gender'] = df['patient'].apply(lambda x: x.get('patientsex') if isinstance(x, dict) else None)
        df['onset_age'] = df['patient'].apply(lambda x: x.get('patientonsetage') if isinstance(x, dict) else None)

        # Drop the nested columns
        df.drop(columns=['primarysource', 'sender', 'receiver', 'patient'], inplace=True, errors='ignore')

        # Step 4: Keep only required columns
        needed_columns = [
            'safetyreportid', 'primarysourcecountry', 'occurcountry', 'transmissiondate',
            'reporttype', 'serious', 'seriousnesshospitalization', 'receivedateformat',
            'source_qualification', 'sender_org', 'receiver_org',
            'onset_age', 'weight_kg', 'gender'
        ]
        df = df[needed_columns]

        # Step 5: Convert data types
        df['transmissiondate'] = pd.to_datetime(df['transmissiondate'], format='%Y%m%d', errors='coerce')
        df['receivedateformat'] = pd.to_datetime(df['receivedateformat'], format='%Y%m%d', errors='coerce')
        df['onset_age'] = pd.to_numeric(df['onset_age'], errors='coerce')
        df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce')
        df['onset_age'] = df['onset_age'].astype('Int64')

        # Step 6: Handle missing values
        df.fillna({
            'weight_kg': df['weight_kg'].mean(),
            'onset_age': df['onset_age'].median(),
            'sender_org': 'Unknown',
            'receiver_org': 'Unknown',
            'gender': 'Unknown',
            'source_qualification': 'Unknown'
        }, inplace=True)

        # Step 7: Drop invalid rows
        df = df[(df['onset_age'] < 120) & (df['weight_kg'] < 300)]

        # Step 8: Add age group column
        df['age_group'] = pd.cut(
            df['onset_age'].astype(float),
            bins=[0, 18, 40, 60, 120],
            labels=['Child', 'Adult', 'Middle Age', 'Senior']
        )

        df.reset_index(drop=True, inplace=True)

        # Step 9: Save final CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        # Create a unique file name using timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = file_key.split('/')[-1].replace('.json', '')

        # Upload cleaned to processed folder
        processed_key = f"{processed_folder}{base_name}_cleaned_{timestamp}.csv"
        s3.put_object(Bucket=bucket_name, Key=processed_key, Body=csv_data)

        # Upload same to analytics_ready
        analytics_key = f"{analytics_folder}{base_name}_analytics_{timestamp}.csv"
        s3.put_object(Bucket=bucket_name, Key=analytics_key, Body=csv_data)

        # Step 10: Delete original raw file
        s3_resource.Object(bucket_name, file_key).delete()

    return {
        'statusCode': 200,
        'body': f"{len(files)} file(s) processed successfully."
    }
