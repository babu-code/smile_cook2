from http import HTTPStatus
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required,create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from utilities import check_password
from models.user import User

black_list = set()

class TokenResource(Resource):
    def post(self):
        json_data = request.get_json()
        email = json_data['email']
        password = json_data['password']

        user = User.get_by_email(email = email)

        if not user or not check_password(password, user.password):
            return {'message': 'email or password is incorrect'}, HTTPStatus.UNAUTHORIZED
        if user.is_active is False:
            return {'message': 'This user account is not activated yet'}, HTTPStatus.FORBIDDEN
        access_token = create_access_token(identity = user.id, fresh = True)
        refresh_token = create_refresh_token(identity = user.id)
        
        return {'access_token': access_token, 'refresh_token':refresh_token}, HTTPStatus.OK

class RefreshResource(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user, fresh = False)
        return {access_token:access_token},HTTPStatus.OK
    
class RevokeResource(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        black_list.add(jti)
        return  {'message':'Succesfully logged out'}, HTTPStatus.OK
    