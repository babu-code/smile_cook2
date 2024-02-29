import os
from flask import Flask, request
from flask_restful import Api
from flask_migrate import Migrate
from flask_restful import Api
from datetime import datetime
from datetime import timedelta
from flask_jwt_extended import get_jwt, create_access_token, get_jwt_identity
from flask_uploads import configure_uploads, patch_request_class
from extensions import db, jwt, image_set, cache, limiter

import config
from extensions import db,jwt
from resources.recipe import RecipeListResource, RecipeResource, RecipePublishResource
from resources.user import UserListResource,UserResource, MeResource, UserRecipeListResource, UserActivateResource, UserAvatarUploadResource
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list

def create_app():

    env = os.environ.get('ENV', 'Development')
    if env == 'Production':
        config_str = 'config.ProductionConfig'
    elif env == 'Staging':
        config_str = 'config.StagingConfig'
    else:
        config_str = 'config.DevelopmentConfig'

    app = Flask(__name__)
    app.config.from_object(config_str)

    # @app.after_request
    # def refresh_token(response):
    #     exp_time = get_jwt()['exp']
    #     target_time = datetime.timestamp(datetime.now() + timedelta(hours=1))
    #     if target_time> exp_time:
    #         access_token = create_access_token(identity=get_jwt_identity())
            
    #     return response

    configure_uploads(app, image_set)
    patch_request_class(app, 10 * 1024 * 1024)

    register_extensions(app)
    register_resources(app)
    
    return app
 
def register_extensions(app):
    db.init_app(app)
    migrate = Migrate(app,db)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(self,decrypted_token):
        jti = decrypted_token['jti']
        return jti in black_list
    
    # @app.before_request 
    # def before_request():
    #     print('\n==================== BEFORE REQUEST ====================\n')
    #     print(cache.cache._cache.keys())
    #     print('\n========================================\n')

    # @app.after_request
    # def after_request(response):
    #     print('\n=================== AFTER REQUEST ====================\n')
    #     print(cache.cache._cache.keys()) 
    #     print('\n========================================\n')
    #     return response
    @limiter.request_filter
    def ip_whitelist():
        return request.remote_addr=='127.0.0.1'

def register_resources(app):
    api = Api(app)
    api.add_resource(RecipeListResource, "/recipes")
    api.add_resource(RecipeResource, "/recipes/<int:recipe_id>")
    api.add_resource(RecipePublishResource, "/recipes/<int:recipe_id>/publish")
    
    api.add_resource(UserListResource, "/users")
    api.add_resource(UserResource, "/users/<string:username>")
    api.add_resource(MeResource, "/me")
    api.add_resource(UserRecipeListResource, '/users/<string:username>/recipes')
    api.add_resource(UserActivateResource, '/users/activate/<string:token>')
    api.add_resource(UserAvatarUploadResource, '/users/avatar')
    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)