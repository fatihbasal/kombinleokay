from flask import request, jsonify, send_file
import boto3
from flask_smorest import Blueprint
from io import BytesIO
from db import db
from models import ClotheModel

s3_bp = Blueprint('s3', __name__)

    
#S3 configuration
S3_BUCKET = 'kombinle'
s3 = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,
aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


#upload to S3
@s3_bp.route('/upload/<int:user_id>', methods=['POST'])
def upload_file(user_id):
    file = request.files['file']
    
    if not file:
            return jsonify({'error': 'No file part'}), 400
        
    if file.filename == ' ':
        return jsonify({'error':'No selected file'})
    
    print(user_id)
    
    s3.upload_fileobj(file,S3_BUCKET,file.filename)
    
    object_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file.filename}"

     # Yeni ClotheModel nesnesi oluşturma
    new_clothe = ClotheModel(
        image_url=object_url,
        color="",
        size="",
        brand="",
        type="",
        sex="",
        user_id=user_id
    )
    db.session.add(new_clothe)
    db.session.commit()
    return jsonify(new_clothe.to_dict())


@s3_bp.route('/image/<filename>')
def get_image(filename):
    try:
        # Get the file from S3
        file_stream = BytesIO()
        s3.download_fileobj(S3_BUCKET, filename, file_stream)
        file_stream.seek(0)  # Move to the start of the stream
        return send_file(file_stream, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 404