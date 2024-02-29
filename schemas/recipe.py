from marshmallow import Schema, fields, validate, validates, post_dump,ValidationError
from schemas.user import UserSchema

from sqlalchemy import asc, desc


class RecipeSchema(Schema):
    id = fields.Int(dump_only= True)
    name = fields.String( validate=[validate.Length(max = 100)])
    cook_time = fields.Int()
    description = fields.String()
    directions = fields.String()
    is_publish = fields.Boolean(dump_only = True)
    author = fields.Nested(UserSchema, attribute='user', dump_only = True, only =['id', 'username'])
    created_at = fields.DateTime(dump_only =True)
    updated_at = fields.DateTime(dump_only = True)
    
    def validate_num_of_servings(n):
        if n<1:
            raise ValidationError('Number of servings must be greater than 0')
        if n>50:
            raise ValidationError('Number of servings must be less than 50')
        
    num_of_servings = fields.Int(required=True, validate=validate_num_of_servings)

    @validates('cook_time')
    def validate_cook_time(self,value):
        if value<1:
            raise ValidationError('Cook time must be greater than 0')
        if value > 300:
            raise ValueError('Cook time must not be greater than 300')
        
from schemas.pagination import PaginationSchema      
class RecipePaginationSchema(PaginationSchema):
    data = fields.Nested(RecipeSchema, attribute = 'items', many = True)

    @classmethod
    def get_all_published(cls, page, per_page):
        return cls.query.filter_by(is_publish=True).order_by(desc(cls.created_at)).paginate(page=page, per_page=per_page) 
    
