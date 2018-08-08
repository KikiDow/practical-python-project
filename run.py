import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

app.secret_key = "key"
"""Security is not a requirement of this project."""

app_info = {
    "username": "",
    "all_users": "",
    "register": "",
    "check_availability_active": "",
    "register_button_active": ""
}

def write_to_file(filename, data):
    """Handle the process of writing data to a file"""
    with open(filename, "a") as file:
        file.writelines(data)
        
def read_users(filename):
    """Read data from file"""
    user_list = []
    file = "data/" + filename
    with open(file, "r") as readfile:
        user_list = readfile.read()
        #user_list = readfile.readlines()
    return user_list
    
def check_user(data, user):
    """Check to see if user is in list of users"""
    for item in data:
        if item == user:
            return True


@app.route('/', methods=['GET','POST'])
def index():
    login_feedback = ""
    if request.method == "POST":
        app_info["username"] = request.form['username']
        app_info["all_users"] = read_users("users.txt")
        if app_info["username"] == "":
            login_feedback = "You must enter a username to login."
            return render_template("index.html", login_feedback=login_feedback)
        elif app_info["username"] in app_info["all_users"]:
            return redirect(url_for('user'))
        #login_feedback = app_info["all_users"]
        else:
            login_feedback = "Username does not exist."
            return render_template("index.html", login_feedback=login_feedback)
    return render_template("index.html", login_feedback=login_feedback)
    

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact', methods=['GET','POST'])
def contact():
    return render_template("contact.html")
    

@app.route('/scoreboard')
def scoreboard():
    return render_template("scoreboard.html")
    
@app.route('/register', methods=['GET','POST'])
def register():
    register_feedback = ""
    app_info["register_button_active"] = "btn-deactivated btn-hide"
    if request.method == "POST":
        app_info["username"] = request.form["username"]
        app_info["all_users"] = read_users("users.txt")
        if 'check_availability' in request.form:
            if app_info["username"] == "" or len(app_info["username"]) < 3:
                app_info["register"] = ""
                app_info["register_button_active"] = "btn-deactivated btn-hide"
                app_info["check_availability_active"] = ""
                register_feedback = "You must enter a username of at least three characters to register."
                #return render_template("register.html", register_feedback=register_feedback)    
            elif app_info["username"] in app_info["all_users"]:
                app_info["register"] = ""
                app_info["register_button_active"] = "btn-deactivated btn-hide"
                app_info["check_availability_active"] = ""
                register_feedback = "That username is not available, please try another."
                #return render_template("register.html", register_feedback=register_feedback)
            else:
                app_info["register"] = "register"
                app_info["register_button_active"] = ""
                app_info["check_availability_active"] = "btn-deactivated btn-hide"
                register_feedback = app_info["username"] + " available, click Register button to continue."
                #return render_template("register.html", register_feedback=register_feedback)
            return render_template("register.html", app_info=app_info, register_feedback=register_feedback)
        if "register" in request.form:
            if app_info["username"] == "":
                app_info["register"] = ""
                app_info["register_button_active"] = "btn-deactivated btn-hide"
                app_info["check_availability_active"] = ""
                register_feedback = "You need to enter a username first."
                return render_template("register.html", app_info=app_info, register_feedback=register_feedback)
            else:
                write_to_file("data/users.txt", app_info["username"] + "\n")
                return redirect(url_for('user'))
    app_info["register"] = "register"
    app_info["all_users"]=""
    return render_template("register.html", app_info=app_info)

@app.route('/user')
def user():
    username_feedback = app_info["username"].capitalize()
    return render_template("user.html", username_feedback=username_feedback)

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)