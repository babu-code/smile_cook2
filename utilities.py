# from passlib.hash import pbkdf2_sha256
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import secrets
import os

from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
from extensions import cache


def hash_password(password):
    # return pbkdf2_sha256.hash(password)
    return generate_password_hash(password)

def check_password(password, hashed):
    # return pbkdf2_sha256.verify(password, hashed)
    return check_password_hash(hashed, password)
def generate_token(email, salt=None):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    return serializer.dumps(email, salt = salt)

@staticmethod
def verify_token(token, max_age=30*60, salt=None):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))

    try:
        email = serializer.loads(token)["id"]
    except:
        return False
    return email

def save_image(image):
    
    _, f_ext = os.path.splitext(image.filename)
    rand_name = secrets.token_hex(8)
    new_fname = str(rand_name) + f_ext

    img_path = os.path.join(os.getcwd(),'static/images/avatars', new_fname )
    
    output_size = (300,300)
    i =Image.open(image)
    i.thumbnail(output_size)
    i.save(img_path)
    
    return new_fname

def clear_cache(key_prefix):
    keys = [key for key in cache.cache._cache.keys() if key.startswith(key_prefix)]
    cache.delete_many(*keys)