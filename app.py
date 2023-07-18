from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
import configparser
from datetime import datetime

# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)

# Reads from the passwords.config file to get the connection string
configParser = configparser.ConfigParser()
configParser.read("passwords.config")


app.config["SQLALCHEMY_DATABASE_URI"] = configParser["SERVERCONFIG"]["ConnectionString"]

# initialize the app with the extension
db.init_app(app)

class Users(db.Model):
    __tablename__ = "users"
    """This class represents the Users table in the database"""
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String)
    updated_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Integer)
    is_admin = db.Column(db.Boolean, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Orders(db.Model):
    __tablename__ = "orders"
    """This class represents the Orders table in the database"""
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    item_name = db.Column(db.String, nullable=False)
    item_count = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/users")
def users():
    #queries the entire table
    usersList = Users.query.order_by(Users.id)
    #gets a single value from the table as a dict that will be used to get column names
    columnList = list(usersList)[0].as_dict()

    return render_template("users.html", users=usersList, columns=columnList)


@app.route("/updateuser", methods=['GET','POST'])
def updateUserMenu():
    if request.method == 'GET':
        return render_template("update_user.html", user=None, id=None)
    else:
        # Gets the user that is updated from the ID that was entered in the form
        change_user = Users.query.filter_by(id=request.form['id']) if Users.query.filter_by(id=request.form['id']) != None else None

        # When the user enters an ID for the first time, they do not pass any of the update
        # information. The try block only runs when the information is entered as to not cause a
        # BadRequest error.
        try:
            email = request.form['email']
            phone_number = request.form['phone_number']
            status = int(request.form['status'])
            is_admin = eval(request.form['is_admin'])
            
            # Takes the user entered and updates them with all the data entered
            change_user.update({
                'email': email,
                'phone_number': phone_number,
                'status': status,
                'is_admin': is_admin,
                'updated_at': datetime.now()
                })

            db.session.commit()

        except:
            pass
        # convert user into dict
        try:
            final_user = list(change_user)[0].as_dict() 
        except:
            final_user = None

        #user= the user that needs to be changed converted into a dict
        return render_template("update_user.html", user=final_user, id=int(request.form['id']))



@app.route("/adduser", methods=['GET','POST'])
def addUser_add():
    if request.method == 'GET':
        return render_template("add_user.html")
    else:
        #Creates a new user object from the data entered in the form
        new_user = Users(
            #The id was set to AUTO_INCREMENT in the database so it does not need to be added
            email = request.form['email'],
            phone_number = request.form['phone_number'],
            updated_at = datetime.now(),
            status = request.form['status'],
            is_admin = bool(int(request.form['is_admin']))
        )

        db.session.add(new_user)
        db.session.commit()

        return render_template("add_user.html")
        


@app.route("/deleteuser", methods=['GET','POST'])
def deleteUser():
    if request.method == 'GET':
        return render_template("delete_user.html")
    else:
        # Gets the id entered in the form and deletes the corresponding orders of the user.
        # Orders need to be deleted first since they are dependent on the user.
        Orders.query.filter_by(user_id=request.form['id']).delete()

        #Deletes the user
        Users.query.filter_by(id=request.form['id']).delete()
        db.session.commit()

        return render_template("delete_user.html")


@app.route("/orders")
def orders():
    # Gets the user_id from the query string sent from the orders table
    reqArgs = request.args
    id = reqArgs['id'] if 'id' in reqArgs.keys() else None

    # Query the orders that match the user_id
    userOrders = Orders.query.filter_by(user_id=id)
    # Get the name of the columns from orders
    columnList = list(userOrders)[0].as_dict() if list(userOrders) != [] else None

    return render_template("orders.html", id=id, orders=userOrders, columns=columnList)

# app.run(debug=True)