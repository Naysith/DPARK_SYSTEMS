from flask import Blueprint, request
from app.function import (
    create_user,
    get_all_users,
    get_user_by_id,
    update_user,
    delete_user
)

main_bp = Blueprint('main', __name__)

# CRUD Routes for Users
@main_bp.route('/users', methods=['POST'])
def route_create_user():
    return create_user(request.get_json())

@main_bp.route('/users', methods=['GET'])
def route_get_users():
    return get_all_users()

@main_bp.route('/users/<int:user_id>', methods=['GET'])
def route_get_user(user_id):
    return get_user_by_id(user_id)

@main_bp.route('/users/<int:user_id>', methods=['PUT'])
def route_update_user(user_id):
    return update_user(user_id, request.get_json())

@main_bp.route('/users/<int:user_id>', methods=['DELETE'])
def route_delete_user(user_id):
    return delete_user(user_id)
