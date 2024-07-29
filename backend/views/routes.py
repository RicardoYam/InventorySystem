from flask import Blueprint, jsonify, request, current_app
from models.models import db, User, UserRole, ProductSize, Product, Stock
from utils.utils import hash_password, check_password, token_required, JWT_KEY
import jwt
import datetime

api = Blueprint('api', __name__, url_prefix='/api/v1')

S3_BUCKET = 'joyshowtest'
S3_REGION = 'us-east-1'

@api.route('/health')
def health():
    try:
        return jsonify({'healthy': True}), 200
    except:
        return jsonify({'healthy': False}), 500
    
    
@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username and not password:
        return jsonify({"message": "Missing fields"}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User doesn't exist"}), 400
    
    if not check_password(password, user.password):
        return jsonify({"message": "Password incorrect"}), 400
    
    token = jwt.encode({"user_id": user.id},
                        JWT_KEY,
                        "HS256")
    
    return jsonify({"message": "Login success", "username": user.username, "token": token}), 200

    
@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    isAdmin = data.get('isAdmin')

    if not username or not password or isAdmin is None:
        return jsonify({"message": "Missing fields"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400
    
    salt, password = hash_password(password)

    if isAdmin:
        new_user = User(username=username, salt=salt, password=password, role = UserRole.ADMIN)
    else:
        new_user = User(username=username, salt=salt, password=password, role = UserRole.USER)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 200


@api.route('/addStock', methods=['POST'])
# @token_required
def add_stock():
    """
    POST: Adding stock to the inventory.

    This endpoint adds a new product to the inventory with its corresponding stock
    details such as size, color, and quantity. An optional image can also be uploaded
    for the product.

    Expected JSON format:
    {
        "name": <str>, # required
        "productDict": {
            "<size>": {
                "<color>": <int> # quantity
            }
        }, # required
        "purchasedPrice": <float>, # required
        "sellingPrice": <float>, # required
    }
    The optional image file should be included in the request as a multipart/form-data part
    with the key "image".

    JSON format for the response to the client:
    {
        "message": "Product and stock added successfully"
    }
    If any required fields are missing or an error occurs, an appropriate error message
    will be returned.

    Args:
        None

    Raises:
        Exception: If any other error occurs during the process.

    Returns:
        str: JSON response with a message indicating the result of the operation.
    """
    
    try:
        # Retrieve JSON data
        data = request.get_json()
        name = data.get('name')
        product_dict = data.get('productDict')
        purchased_price = data.get('purchasedPrice')
        selling_price = data.get('sellingPrice')
        image_name = None
        image_url = None
        image_type = None

        if not name or not product_dict or not purchased_price or not selling_price:
            return jsonify({"message": "Missing fields"}), 400

        if 'image' in request.files:
            image = request.files['image']
            image_name = image.filename
            image_type = image.content_type
            try:
                # TODO: UPLOAD to s3 (this part is a placeholder, you need to implement S3 upload logic)
                # image_url = f'https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{image.filename}'
                pass
            except Exception as e:
                return jsonify({"message": f"Failed to upload image: {str(e)}"}), 500

        new_product = Product(
            name=name,
            purchased_price=float(purchased_price),
            selling_price=float(selling_price),
            image_name=image_name,
            image_url=image_url,
            image_type=image_type
        )

        db.session.add(new_product)
        db.session.commit()

        for size, colors in product_dict.items():
            for color, quantity in colors.items():
                new_stock = Stock(
                    product_id=new_product.id,
                    color=color,
                    size=ProductSize[size],
                    quantity=quantity,
                    create_time=datetime.datetime.now()
                )
                db.session.add(new_stock)
        db.session.commit()

        return jsonify({"message": "Product and stock added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to add product: {str(e)}"}), 500


@api.route('/protected', methods=['GET'])
@token_required
def protected_route(user_id):
    return jsonify({"message": f"Hello, user {user_id}!"})