from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_, desc, asc

from models.recipe import Recipe
from webargs import fields
from webargs.flaskparser import use_kwargs
from schemas.recipe import RecipeSchema, RecipePaginationSchema
from extensions import cache, limiter
from utilities import clear_cache

recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)
recipe_resource_schema = RecipeSchema()
recipe_pagination_schema = RecipePaginationSchema()



class RecipeListResource(Resource):
    
    decorators = [limiter.limit('100 per minute', methods=['GET'], error_message = 'Too many Requests')]
    @use_kwargs({
        'q': fields.Str(missing=''),
        'page':fields.Int(missing=1),
                  'per_page': fields.Int(missing=1),
                  })
    @cache.cached(timeout=60, query_string=True)
    def get(self,q,page, per_page):
        print('Querying database...')
        q = request.args.get('q')  
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        
        # paginated_recipes =  Recipe.query.filter(or_(Recipe.name.ilike(q),
        #                     Recipe.description.ilike(q))).\
        # order_by(desc(Recipe.created_at)).paginate(page=page,per_page=per_page)
        if q is None:
            q = ""
        paginated_recipes =Recipe.query.filter(Recipe.name.icontains(q)|
                Recipe.description.ilike(q)).\
                order_by(Recipe.created_at.desc()).paginate(page=page,
                per_page=per_page)
        
        return recipe_pagination_schema.dump(paginated_recipes), HTTPStatus.OK
    
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        data= recipe_schema.load(data=json_data)
        current_user = get_jwt_identity()
        # if errors:
        #     return {'message': "validation errors", 'errors':errors}, HTTPStatus.BAD_REQUEST
        recipe = Recipe(**data )
        recipe.user_id = current_user
        recipe.save()

        return recipe_schema.dump(recipe), HTTPStatus.CREATED  


class RecipeResource(Resource):
    @jwt_required(optional = True)
    def get(self, recipe_id):
        recipe =  Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {"message": 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.is_publish == False and recipe.user_id != current_user:
            return {'message': "Access is not allowed"}, HTTPStatus.FORBIDDEN
        return recipe_resource_schema.dump(recipe), HTTPStatus.FOUND
    
    @jwt_required()
    def put(self, recipe_id):
        data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id=recipe_id)   
        if not recipe:
            return {"message": 'recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if recipe.user_id != current_user:
            return {'message': 'access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.name = data["name"]
        recipe.description = data["description"]
        recipe.num_of_servings = data["num_of_servings"]
        recipe.cook_time = data["cook_time"]
        recipe.directions = data["directions"]

        clear_cache('/recipes')

        return recipe_resource_schema.dump(recipe), HTTPStatus.OK
    @jwt_required()
    def patch(self, recipe_id):
        json_data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id)
        recipe_schema = RecipeSchema()
        data=recipe_schema.load(json_data, partial=('name',))
        if not recipe:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        if current_user !=recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN
        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions
        recipe.save()

        clear_cache('/recipes')

        return recipe_schema.dump(recipe), HTTPStatus.OK

    @jwt_required(optional= True)
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if not recipe:
            return {'message': 'recipe not found'}
        current_user = get_jwt_identity()
        if recipe.user_id !=current_user:
            return {'message':'Access not allowed'}, HTTPStatus.FORBIDDEN
        recipe.delete()

        clear_cache('/recipes')

        return {}, HTTPStatus.NO_CONTENT

class RecipePublishResource(Resource):
    def put(self, recipe_id):
        recipe = next((recipe for recipe in recipe_list if recipe.id == recipe_id), None)
        if recipe is None:
            return {"message": 'recipe not found'}, HTTPStatus.NOT_FOUND
        recipe.is_publish = True
        
        clear_cache('/recipes')

        return {}, HTTPStatus.NO_CONTENT
    def delete(self, recipe_id):
        recipe = next((recipe for recipe in recipe_list if recipe.id == recipe_id), None)
        if recipe is None:
            return {"message": 'recipe not found'}, HTTPStatus.NOT_FOUND
        recipe.is_publish = False
        
        clear_cache('/recipes')

        return {}, HTTPStatus.NO_CONTENT