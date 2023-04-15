from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self):
        return f"Cafe ID:{self.id} "


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def get_random_cafe():
    cafes = Cafe.query.all()
    print("THIS >>")
    print(cafes)
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    cafes = Cafe.query.all()
    # This uses a List Comprehension but you could also split it into 3 lines.
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = Cafe.query.filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(
            error={
                "Not Found": "Sorry, we don't have a cafe at that location."
            }
        )


# HTTP POST - Create Record / HTTP GET - Read Record


@app.route("/cafe", methods=["POST"])
@app.route("/cafe/<int:cafe_id>")
def post_new_cafe(cafe_id=None):
    if request.method == "GET":
        # Query the database for the user with the given ID
        cafe = Cafe.query.get(cafe_id)

        # If the user does not exist, return an error with a 404 status code
        if not cafe:
            return jsonify(error=f"Cafe with id {cafe_id} not found."), 404

        # If the user exists, return the user object as a JSON response
        return jsonify(cafe=cafe.to_dict())
    elif request.method == "POST":
        # Get the JSON data from the request body
        data = request.get_json()

        # Create a dictionary of attribute names and values from the JSON data
        cafe_data = {key: value for key, value in data.items()}

        # Create a new User object and initialize it with the dictionary
        cafe = Cafe(**cafe_data)

        # Add the User object to the database
        db.session.add(cafe)
        db.session.commit()

        # Return the updated user object as a JSON response
        return jsonify(cafe=cafe.to_dict())


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_user_age(cafe_id):
    # Get the JSON data from the request body
    data = request.get_json()

    # Query the database to get the User object with the given id
    cafe = Cafe.query.filter_by(id=cafe_id).first()
    if cafe:
        # Update the age of the User object with the new age value from the JSON data
        cafe.coffee_price = data["coffee_price"]

        # Commit the changes to the database
        db.session.commit()
        return jsonify(cafe=cafe.to_dict())

    return {"error": f"Coffee with id{cafe_id} not found."}, 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    if not cafe:
        # Return an error response if the user doesn't exist
        return jsonify(error=f"Cafe with id {cafe_id} not found."), 404

    # Delete the user from the database
    db.session.delete(cafe)
    db.session.commit()
    return jsonify(message="Cafe deleted successfully")


if __name__ == "__main__":
    app.run(debug=True)
