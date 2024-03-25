from bson import ObjectId
from flask import Flask, request, jsonify
from pymongo import MongoClient
import re

app = Flask(__name__)

# MongoDB Atlas setup
client = MongoClient('mongodb+srv://parthgajera056:parth1234@t7cluster.udmh9ec.mongodb.net/?retryWrites=true&w=majority&appName=T7cluster')
db = client['T7_Users']
users_collection = db['users']

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def user_db_to_dict(user):
    user['_id'] = str(user['_id'])  # Convert ObjectId to string for JSON serialization
    return user

def add_default_users():
    default_users = [
        {"firstName": "Parth", "email": "parth.gajera@dal.ca"},
        {"firstName": "Darshan", "email": "darshan.patel@dal.ca"}
    ]
    for user in default_users:
        if not users_collection.find_one({"email": user["email"]}):
            users_collection.insert_one(user)

@app.route('/users', methods=['GET'])
def get_all_users():
    users_cursor = users_collection.find()
    users_list = [user_db_to_dict(user) for user in users_cursor]
    return jsonify({
        "message": "Users retrieved",
        "success": True,
        "users": users_list
    })

@app.route('/add', methods=['POST'])
def add_user():
    data = request.json
    if 'firstName' not in data or 'email' not in data:
        return jsonify({"message": "Missing data", "success": False}), 400
    if not is_valid_email(data.get('email')):
        return jsonify({"message": "Invalid email address", "success": False}), 400
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"message": "User with this email already exists", "success": False}), 400

    new_user = {"firstName": data['firstName'], "email": data['email']}
    users_collection.insert_one(new_user)
    return jsonify({"message": "User added", "success": True}), 201


@app.route('/update/<id>', methods=['PUT'])
def update_user(id):
    user_id = ObjectId(id)
    data = request.json
    update_data = {}
    if 'firstName' in data:
        update_data['firstName'] = data['firstName']
    if 'email' in data:
        if not is_valid_email(data['email']):
            return jsonify({"message": "Invalid email address", "success": False}), 400
        update_data['email'] = data['email']
    result = users_collection.update_one({"_id": user_id}, {"$set": update_data})
    if result.matched_count:
        return jsonify({"message": "User updated", "success": True})
    else:
        return jsonify({"message": "User not found", "success": False}), 404

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user_id = ObjectId(id)
    user = users_collection.find_one({"_id": user_id})
    if user:
        return jsonify({"success": True, "user": user_db_to_dict(user)})
    else:
        return jsonify({"message": "User not found", "success": False}), 404


@app.route('/delete/<id>', methods=['DELETE'])
def delete_user(id):
    user_id = ObjectId(id)
    result = users_collection.delete_one({"_id": user_id})
    if result.deleted_count:
        return jsonify({"success": True, "message": "User deleted"}), 200
    else:
        return jsonify({"message": "User not found", "success": False}), 404

if __name__ == '__main__':
    add_default_users()  # Add default users on app start
    app.run(host="0.0.0.0", port=5000, debug=True)
