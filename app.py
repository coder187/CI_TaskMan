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

@app.route("/search", methods=['POST', 'GET'])
def search():
    query = request.form.get("query")
    tasks = list(mongo.db.tasks.find({"$text": {"$search":query}}))
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


@app.route("/add_task.html", methods=['POST', 'GET'])
def add_task():
    # if POST then  add record
    # ELSE GET then return list of Categories for combo box
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        print(request.form.get("category_name"))
        task = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_descriptio": request.form.get("task_description"),   
            "due_date": request.form.get("due_date"),
            "is_urgent": is_urgent,
            "created_by": session["user"]
        }   

        mongo.db.tasks.insert_one(task)
        flash("Task Inserted Successfully")
        return redirect(url_for("get_tasks"))

    categories = mongo.db.categories.find().sort("category_name",1)
    return render_template("add_task.html",categories=categories)


@app.route("/edit_task/<task_id>", methods=['POST', 'GET'])
def edit_task(task_id):

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    if request.method == "POST":
        
        is_urgent = "on" if request.form.get("is_urgent") else "off"

        submit = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_descriptio": request.form.get("task_description"),    
            "due_date": request.form.get("due_date"),
            "is_urgent": is_urgent,
            "created_by": session["user"]
        }   

        mongo.db.tasks.update({"_id": ObjectId(task_id)},submit)
        flash("Task Udated Successfully")

    categories = mongo.db.categories.find().sort("category_name",1)
    return render_template("edit_task.html", task=task,categories=categories)

@app.route("/delete_task/<task_id>")
def delete_task(task_id):
    mongo.db.tasks.remove({"_id": ObjectId(task_id)})
    flash("Task Successfully Deleted")
    return redirect(url_for("get_tasks"))


@app.route("/get_categories.html")
def get_categories():
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    if session["user"].lower() != "admin":
        return redirect(url_for("login"))
    
    categories = list(mongo.db.categories.find().sort("category_name",1))
    return render_template("get_categories.html", categories=categories)


@app.route("/add_category.html", methods=['POST', 'GET'])
def add_category():
    if session["user"].lower() != "admin":
        return redirect(url_for("login"))
    
    if request.method == "POST":
        category = {
            "category_name": request.form.get("category_name")
        }
        mongo.db.categories.insert_one(category)
        flash("Category Added Successfully")
        return redirect(url_for("get_categories"))

    return render_template("add_category.html")

@app.route("/delete_category<category_id>")
def delete_category(category_id):
    if session["user"].lower() != "admin":
        return redirect(url_for("login"))
    
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))

@app.route("/edit_category<category_id>", methods=['POST', 'GET'])
def edit_category(category_id):
    if session["user"].lower() != "admin":
        return redirect(url_for("login"))

    if request.method == "POST":
        submit = {"category_name":request.form.get("category_name")}
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Updated Successfully")
        return redirect(url_for("get_categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("edit_category.html", category=category)


# set host and ip from env.py
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)