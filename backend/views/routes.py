from flask import Blueprint, jsonify, request, current_app
from models.models import db, User, UserRole, ProductSize, Product, Stock
from utils.utils import hash_password, check_password, token_required, JWT_KEY
import jwt
import datetime

api = Blueprint("api", __name__, url_prefix="/api/v1")

S3_BUCKET = "joyshowtest"
S3_REGION = "us-east-1"


@api.route("/health")
def health():
    try:
        return jsonify({"healthy": True}), 200
    except:
        return jsonify({"healthy": False}), 500


@api.route("/login", methods=["POST"])
def login():
    """
    POST: User Login.

    Handles user login by validating the provided username and password against
    the stored user data. If the credentials are valid, a JWT token is generated
    and returned to the client.

    Expected JSON format:
    {
        "username": <str>,   # required
        "password": <str>    # required
    }

    JSON format for the response to the client:
    On success:
    {
        "message": "Login success",
        "username": <str>,    # The username of the logged-in user
        "token": <str>        # JWT token for authentication
    }

    On failure:
    {
        "message": <str>   # Error message indicating the reason for failure
    }

    Raises:
        Exception: For any errors encountered during login.

    Returns:
        Response: JSON response with a message indicating the result of the operation.
                  Status code 200 on success, 400 on failure.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username and not password:
        return jsonify({"message": "Missing fields"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"message": "User doesn't exist"}), 400

    if not check_password(password, user.password):
        return jsonify({"message": "Password incorrect"}), 400

    token = jwt.encode({"user_id": user.id}, JWT_KEY, "HS256")

    return jsonify({"message": "Login success", "username": user.username, "token": token}),200


@api.route("/register", methods=["POST"])
def register():
    """
    POST: User Registration.

    Handles the registration of a new user. The function checks for the presence of
    required fields (username, password, and is_admin) in the request data, validates
    the uniqueness of the username, hashes the password, and creates a new user record
    in the database.

    Expected JSON format:
    {
        "username": <str>,   # required
        "password": <str>,   # required
        "is_admin": <bool>   # required, indicates if the user is an admin
    }

    JSON format for the response to the client:
    On success:
    {
        "message": "User registered successfully"
    }

    On failure:
    {
        "message": <str>   # Error message indicating the reason for failure
    }

    Raises:
        KeyError: If any of the required fields are missing.
        Exception: For any other errors encountered during user registration.

    Returns:
        Response: JSON response with a message indicating the result of the operation.
                  Status code 200 on success, 400 on failure.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    is_admin = data.get("is_admin")

    if not username or not password or is_admin is None:
        return jsonify({"message": "Missing fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    salt, password = hash_password(password)

    if is_admin:
        new_user = User(
            username=username, salt=salt, password=password, role=UserRole.ADMIN
        )
    else:
        new_user = User(
            username=username, salt=salt, password=password, role=UserRole.USER
        )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 200


@api.route("/addStock", methods=["POST"])
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
                "<color>": <quantity>
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

    Raises:
        Exception: If any other error occurs during the process.

    Returns:
        str: JSON response with a message indicating the result of the operation.
    """

    try:
        data = request.get_json()
        name = data.get("name")
        product_dict = data.get("productDict")
        purchased_price = data.get("purchasedPrice")
        selling_price = data.get("sellingPrice")
        image_name = None
        image_url = None
        image_type = None

        if not name or not product_dict or not purchased_price or not selling_price:
            return jsonify({"message": "Missing fields"}), 400

        if "image" in request.files:
            image = request.files["image"]
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
            image_type=image_type,
        )

        db.session.add(new_product)
        db.session.commit()

        for size, colors in product_dict.items():
            for color, quantity in colors.items():
                new_stock = Stock(
                    product_id=new_product.id,
                    color=color.capitalize(),
                    size=size,
                    quantity=quantity,
                    create_time=datetime.datetime.now(),
                )
                db.session.add(new_stock)
        db.session.commit()

        return jsonify({"message": "Product and stock added successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Failed to add product: {str(e)}"}), 500


@api.route("/stocks", methods=["GET"])
def list_stocks():
    """
    Event: List all products with their stock information, with pagination and optional name and size filtering.

    Retrieves all products from the database along with their associated stocks
    and returns them in JSON format. Supports pagination and filtering by product name and size.

    Query Parameters:
        page (int): The page number to retrieve. Default is 1.
        per_page (int): The number of items per page. Default is 10.
        name (str): Optional. The name of the product to search for. Case insensitive partial match.
        size (str): Optional. The size of the product to filter by. Must be one of 'S', 'M', 'L', 'XL'.

    JSON format for the response to the client:
    {
        "data": [
            {
                "id": <int>,
                "name": <str>,
                "purchased_price": <float>,
                "selling_price": <float>,
                "image_url": <str>,
                "stocks": [
                    {
                        "id": <int>,
                        "color": <str>,
                        "size": <str>,
                        "quantity": <int>
                    }
                ]
            }
        ],
        "colors": [<str>],  # List of unique colors found in the stocks
        "sizes": [<str>],   # List of all possible sizes from ProductSize enum
        "total": <int>,     # Total number of products matching the filters
        "pages": <int>,     # Total number of pages based on the current per_page setting
        "current_page": <int>  # Current page number
    }

    Raises:
        KeyError: If the provided size is not a valid enum value.
        Exception: For any other errors encountered during data retrieval.

    Returns:
        Response: JSON response with the list of products and their stock information.
    """

    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        name = request.args.get("name", type=str)
        size = request.args.get("size", type=str)

        # Base query
        query = db.session.query(Product)

        # Filter by name if provided
        if name:
            query = query.filter(Product.name.ilike(f"%{name}%"))

        # Filter by size if provided
        if size:
            try:
                size_enum = ProductSize[size.upper()]
                query = query.join(Product.stocks).filter(Stock.size == size_enum)
            except KeyError:
                return jsonify({"message": f"Invalid size: {size}"}), 400

        # Paginate the results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        products = pagination.items

        response_data = []
        unique_colors = set()
        for product in products:
            product_data = {
                "id": product.id,
                "name": product.name,
                "purchased_price": product.purchased_price,
                "selling_price": product.selling_price,
                "image_url": product.image_url,
                "stocks": (
                    [
                        {
                            "id": stock.id,
                            "color": stock.color,
                            "size": stock.size.name,
                            "quantity": stock.quantity,
                        }
                        for stock in product.stocks
                        if stock.size == size_enum
                    ]
                    if size
                    else [
                        {
                            "id": stock.id,
                            "color": stock.color,
                            "size": stock.size.name,
                            "quantity": stock.quantity,
                        }
                        for stock in product.stocks
                    ]
                ),
            }
            # Add colors to the unique colors set
            for stock in product.stocks:
                unique_colors.add(stock.color)

            response_data.append(product_data)

        # Convert unique_colors set to list
        unique_colors_list = list(unique_colors)
        size_list = [size.name for size in ProductSize]

        return (
            jsonify(
                {
                    "data": response_data,
                    "colors": unique_colors_list,
                    "sizes": size_list,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "current_page": pagination.page,
                }
            ),
            200,
        )
    except Exception as e:
        current_app.logger.error(f"Failed to retrieve products: {str(e)}")
        return jsonify({"message": f"Failed to retrieve products: {str(e)}"}), 500


@api.route("/protected", methods=["GET"])
@token_required
def protected_route(user_id):
    return jsonify({"message": f"Hello, user {user_id}!"})
