import os
from flask import (Flask, flash, render_template, redirect,
                    request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

# create an instance of Flask and set it to the variable app
app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBANME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

# We need to setup an instance of PyMongo, 
# and add the app into that using something called a constructor method, so type:
mongo = PyMongo(app)


@app.route("/")
@app.route("/get_tasks")
def get_tasks():
    tasks = list(mongo.db.tasks.find())
    # The first 'tasks' is what the template will use, and that's equal to the second 'tasks', 
    # which is our variable defined above.
    return render_template("tasks.html", tasks=tasks)



@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/profile/<username>", methods=['POST', 'GET'])
def profile(username):
    # username = mongo.db.users.find_one(
    #        {"username": session["user"]})["username"]
    # return render_template("profile.html",username=username)
    # why query the db when the session already has the username

    # check for authenitcated user
    # if session["user"]:  # if session user is truthy
    if session.get('user'):
        return render_template("profile.html",username=session["user"])
    
    # if not auhtenitcated redirect to login page
    return redirect(url_for("login"))

@app.route("/login.html", methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            if check_password_hash(
                existing_user["password"],request.form.get("password")):
                    flash("Welcome, {}".format(request.form.get("username")))
                    session["user"] = request.form.get("username").lower()
                    return render_template("profile.html",username=session["user"])



            else:
                flash("Username and/or Password Incorrect")
        
        else:
            flash("Username and/or Password Incorrect")

    return render_template("login.html")


@app.route("/register.html", methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for("register"))
        
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
            }
        mongo.db.users.insert_one(register)

        session["user"] = request.form.get("username").lower()
        flash("Reistration Successful")
        return render_template("profile.html",username=session["user"])

    return render_template("register.html")


@app.route("/add_task.html")
def add_task():
    categories = mongo.db.categories.find().sort("category_name",1)

    return render_template("add_task.html",categories=categories)


# set host and ip from env.py
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)