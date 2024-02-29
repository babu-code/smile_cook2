import os
from flask import request,abort
from flask_restful import Resource
from http import HTTPStatus
from webargs import fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from webargs.flaskparser import use_kwargs
from flask import request, url_for
from mailgun import MailgunApi
from utilities import generate_token, verify_token

from utilities import  save_image
from models.user import User
from models.recipe import Recipe
from schemas.user import UserSchema
from schemas.recipe import RecipeSchema
from config import Config
from schemas.recipe import RecipePaginationSchema





user_schema = UserSchema()
user_avatar_schema = UserSchema(only=('avatar_url',))
user_public_schema = UserSchema(exclude=('email',))
recipe_list_schema = RecipeSchema(many=True)
recipe_pagination_schema = RecipePaginationSchema()

mailgun = MailgunApi(domain="https://api.mailgun.net/v3/sandboxa4c7fef9ea7e4617bb084b71bfb532a9.mailgun.org/messages", api_key='e32fd32058bda5a6f902b35da64c128b-8c8e5529-423025de')

class UserListResource(Resource):
    
    def post(self):
        json_data = request.get_json()

        data= user_schema.load(data = json_data)
        

        if User.get_by_username(data.get('username')):
            return {"message": 'username already taken'}, HTTPStatus.BAD_REQUEST
        if User.get_by_email(data.get('email')):
            return {"message": 'email already taken'}, HTTPStatus.BAD_REQUEST
        

        user = User(**data)
        user.save()
        
        token = generate_token(user.email, salt='activate')
        subject = 'Please confirm your registration'

        link = url_for('useractivateresource', token =token, _external=True)
        text = f'Hi , Thanks for using SmileCook! Please confirm your registration by clicking on this link: {link}'
        
        try:
            mailgun.send_email(to=user.email, 
                           subject=subject,
                           text=text)
            
            print('Email for account confirmation has been sent to you')
        except: 

            print('something went wrong')
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email
            }
        return data, HTTPStatus.CREATED
 

class UserResource(Resource):
    
   @jwt_required(optional=True)
   def get(self, username):
        user = User.get_by_username(username=username)
        if user is None:
            return {'message':'user not found'}

        current_user = get_jwt_identity()
        if current_user == user.id:
            data = user_schema.dump(user)
        else:
            data ={
            'id':user.id,
            'username':user.username,
                       
            }   

        return data, HTTPStatus.OK
   

class MeResource(Resource):
    @jwt_required()
    def get(self):
        user = User.query.filter_by(id=get_jwt_identity()).first()
        data = user_schema.dump(user).data
        return data, HTTPStatus.OK

class UserRecipeListResource(Resource):
    @jwt_required(optional=True)
    @use_kwargs({'visibility':fields.Str(missing='public'),
                 'page':fields.Int(missing=1),
                 'per_page':fields.Int(missing=1)})
    def get(self, username, visibility,page,per_page):
        user = User.get_by_username(username=username)
        
        if not user:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        visibility = request.args.get('visibility')
        page= int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))

        if current_user== user.id and visibility in ['all', 'private']:
            pass            
        else:
            visibility='public'
        recipes = Recipe.get_all_by_user(user_id = user.id,page=page,per_page=per_page, visibility=visibility)
        return recipe_pagination_schema.dump(recipes), HTTPStatus.FOUND
    
class UserAvatarUploadResource(Resource):
    @jwt_required()
    def put(self):
        file = request.files.get('avatar')

        if not file:
            return {'message': 'Not a valid image'}, HTTPStatus.BAD_REQUEST
        
        
        _, f_ext = os.path.splitext(file.filename)
        if f_ext not in Config.ALLOWED_FILE_EXTENSIONS:
            abort("Please ensure that the file you are uploading is an image")
        user = User.query.get( get_jwt_identity())
        if user.avatar_image:
            file_path = os.path.join(os.getcwd(),'static/images/avatars',user.avatar_image )
            os.remove(file_path)
        img = save_image(file)
        user.avatar_image = img
        user.save()

        return user_avatar_schema.dump(user)
    
class UserActivateResource(Resource):
    def get(self, token):
        email = verify_token(token, salt='activate')
        if email is False:
            return {'message': 'Invalid token or token expired'},HTTPStatus.BAD_REQUEST
        user = User.get_by_email(email=email)

        if not user:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND
        
        if user.is_active is True:
            return {'message':'This user account is already activated'}, HTTPStatus.BAD_REQUEST
        user.is_active = True
        user.save()
        return {}, HTTPStatus.NO_CONTENT