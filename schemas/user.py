from marshmallow import Schema, fields
from utilities import hash_password
from flask import url_for



class UserSchema(Schema):
    id = fields.Int(dump_only = True)
    username = fields.String(required = True)
    email = fields.Email(required = True)
    password = fields.Method(required= True, deserialize = 'load_password')
    is_active = fields.Boolean()
    created_at = fields.DateTime(dump_only = True)
    updated_at = fields.DateTime(dump_only = True)
    avatar_url = fields.Method(serialize = 'dump_avatar_url')

    def load_password(self, value):
        return hash_password(value)
    def dump_avatar_url(self, user):
        if user.avatar_image:
            return url_for('static', filename='/images/avatars/{}'.format(user.avatar_image), _external=True)
        else:
            return url_for('static', filename='images/assets/default_avatar.jpg', _external=True)