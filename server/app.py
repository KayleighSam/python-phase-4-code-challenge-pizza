#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

# configure database and environment variables
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

# Initialize Flask application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

#  database migration
migrate = Migrate(app, db)

# Initialize SQLAlchemy AND API
db.init_app(app)

api = Api(app)

#HOME ROUTE
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# Resource for retrieving all restaurants
class Restaurants(Resource):
    def get(self):
        # Query all restaurants and return their details
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(only=("id", "name", "address")) for restaurant in restaurants], 200


# FETCH or delet   e a specific restaurant by ID
class RestaurantById(Resource):
    def get(self, id):
        # Query a specific restaurant by ID
        restaurant = Restaurant.query.get(id)
        if restaurant:
            return restaurant.to_dict(
                only=("id", "name", "address", "restaurant_pizzas.pizza.id", "restaurant_pizzas.pizza.name", "restaurant_pizzas.pizza.ingredients", "restaurant_pizzas.price")
            ), 200
      
        return {"error": "Restaurant not found"}, 404

    def delete(self, id):
        # Delete a specific restaurant by ID
        restaurant = Restaurant.query.get(id)
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return {}, 204  
        
        return {"error": "Restaurant not found"}, 404


# Resource for retrieving all pizzas
class Pizzas(Resource):
    def get(self):
        # Query all pizzas and return their details
        pizzas = Pizza.query.all()
        return [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in pizzas], 200


# Resource for creating a restaurant-pizza relationship
class RestaurantPizzas(Resource):
    def post(self):
        try:
            # Get the JSON payload from the request
            data = request.get_json()
            if not data:
                return {"errors": ["Invalid or missing JSON payload"]}, 400

            # Validate that all required fields are present
            if not all(key in data for key in ["price", "pizza_id", "restaurant_id"]):
                return {"errors": ["Missing required fields: 'price', 'pizza_id', 'restaurant_id'"]}, 400

            # Extract and validate the price
            price = data.get("price")
            if not (1 <= price <= 30):
                return {"errors": ["validation errors"]}, 400

            # Validate that the pizza and restaurant exist
            pizza = Pizza.query.get(data.get("pizza_id"))
            restaurant = Restaurant.query.get(data.get("restaurant_id"))
            if not pizza or not restaurant:
                return {"errors": ["Pizza or Restaurant not found"]}, 404

            # Create and save the restaurant-pizza relationship
            new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=data.get("pizza_id"), restaurant_id=data.get("restaurant_id"))
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            # Return the created relationship
            return new_restaurant_pizza.to_dict(
                only=("id", "price", "pizza.id", "pizza.name", "pizza.ingredients", "restaurant.id", "restaurant.name", "restaurant.address")
            ), 201

        except Exception as e:
            print("Exception occurred:", e)
            return {"errors": [str(e)]}, 500


# Add resources and routes to the API
api.add_resource(Restaurants, "/restaurants")  
api.add_resource(RestaurantById, "/restaurants/<int:id>")  
api.add_resource(Pizzas, "/pizzas") 
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")  


if __name__ == "__main__":
    app.run(port=5555, debug=True)
