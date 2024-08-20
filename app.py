import os
import boto3
import datetime
from flask import Flask, request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
S3_BUCKET = 'cloud-internship-project3-s3'
S3_REGION = 'ap-northeast-1'  # e.g., 'us-east-1'
DYNAMODB_TABLE = 'S3MetadataTable'

# Initialize S3 client
s3 = boto3.client('s3', region_name=S3_REGION)

# Initialize DynamoDB client and resource
dynamodb = boto3.resource('dynamodb', region_name=S3_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        try:
            # Upload file to S3
            s3.upload_fileobj(file, S3_BUCKET, filename)
            
            # Save file info to DynamoDB
            item = {
                'filename': filename,
                's3_bucket': S3_BUCKET,
                's3_key': filename,
                'upload_time': str(datetime.datetime.now())
            }
            table.put_item(Item=item)

            flash('File successfully uploaded to S3 and saved to DynamoDB')
        except Exception as e:
            flash(f'An error occurred: {e}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
