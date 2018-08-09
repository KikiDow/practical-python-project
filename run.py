import os
import json
import ast
import random
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)

app.secret_key = "key"
"""Security is not a requirement of this project."""

app_info = {
    "username": "",
    "all_users": "",
    "register": "",
    "check_availability_active": "",
    "register_button_active": "",
    "logged": False,
    "route": "",
    "game": False
}

best_individual_games = []  # For Hall of Fame
current_game = []           # 
current_riddle = 0
all_riddles = []            # All riddles available for the game
riddle_counter = 0
attempt = 1                 # There are three attempts per riddle.
points = 10
gained_points = 0
wrong_answers =[]           # This will hold wrong answers
answer = ""                 # Current answer of current riddle
user_data = ""     

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
            
def read_from_file(file_name):
    store=""
    file = "data/" + file_name
    with open(file, "r") as readdata:
        store = readdata.read()
    return store
    
def global_game_reset():
    global current_game
    global current_riddle
    global all_riddles
    global riddle_counter
    global attempt
    global points
    global gained_points
    global wrong_answers
    global answer

    current_game = []
    current_riddle = 0
    all_riddles = []
    riddle_counter = 0
    attempt = 1
    points = 10
    gained_points = 0
    wrong_answers =[]
    answer = ""
    
def json_tuple_helper_function(obj):
    """ I added marked tuples with __istuple__ in the json """
    if 'istuple' in obj:
        return tuple(obj['item'])
    else:
        return obj

def find_loggedin_user(data):
    global app_info
    
    username = app_info["username"]
            
    #Need to return an empty set of data
    empty = {
        "user":username,
        "number_of_games":0,
        "date_best_game":"",
        "points_best_game":0,
        "total_user_points":0,
        "games_played":[]}

    if username in data.keys():
        pass
    else:
        data[username] = empty

    return data[username]
    
def fill_best_individual_games():
    global best_individual_games
    store=""
    with open("data/scoreboard_individual.json", "r") as readdata:
        store = readdata.read()  # Read as a string
    store = ast.literal_eval(store) # Turn string to dictionary
    best_individual_games = store["best_individual_games"]

def fill_best_all_games():
    global best_all_games
    store=""
    with open("data/scoreboard_all_games.json", "r") as readdata:
        store = readdata.read()  # Read as a string
    store = ast.literal_eval(store) # Turn string to dictionary
    best_all_games = store["best_all_games"]
    
def sort_current_riddle(data):
    ''' Sort the data so that it is always id, source, answer '''
    ordered_data = [0,0,0]
    for cr in data:   # Select a riddle
        if cr[0] == "id":
            ordered_data[0] = cr[1]
        elif cr[0] == "source":
            ordered_data[1] = cr[1]
        elif cr[0] == "answer":
            ordered_data[2] = ''.join(list(cr[1]))
    return ordered_data

def store_game_info():
    global app_info   # get username
    global gained_points
    global user_data
    
    user_data["number_of_games"] += 1
    user_data["total_user_points"] += gained_points
    
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    info = (today,  gained_points)
    
    extract_games_played = user_data["games_played"]
    # Add next game data
    user_data["games_played"].insert(0, info)
    # Put it back in user_data["games_played"]
     
    if gained_points > user_data["points_best_game"]:
        user_data["points_best_game"] = gained_points
        user_data["date_best_game"] = today   # Today's date
    
    current_json_data = json.loads(read_from_file("user_game_data_json.json"), object_hook=json_tuple_helper_function)
    username = user_data["user"]
    
    current_json_data[username] = user_data
    with open('data/user_game_data_json.json', 'w') as outfile:
        json.dump(current_json_data, outfile,  sort_keys=True, indent=4)
    
    # Update hof_individual.json
    insert=[]
    insert.append(today)
    insert.append(username)
    insert.append(gained_points)
    insert_in_scoreboard_individual(insert)
    # Update hof_all_games.json
    insert_all_games=[]
    insert_all_games.append(username)
    insert_all_games.append(user_data["total_user_points"])
    insert_all_games.append(user_data["number_of_games"])
    insert_in_scoreboard_all_games(insert_all_games)

    return

def insert_in_scoreboard_individual(data):
    global best_individual_games

    # Get list of points from json - already sorted
    sorted_points = [] #Reverse order
    for item in best_individual_games:
        sorted_points.insert(0, item[3])
    
    # Add new points - only if it is more than at least the smallest number 
    if data[2] > min(sorted_points):
        sorted_points.insert(0, data[2])
        sorted_points.sort()
        
        # Reduce length of list to 10 so that I will have the best 10 
        # when I insert the new data
        while len(sorted_points) > 10:
            del sorted_points[0]

        # Build new list of sorted data
        insert_done = False
        
        new_points_list =[]
        counter = len(best_individual_games)-1
        pointer = 0
        
        for item in sorted_points:
            if item == data[2] and insert_done == False: # New item
                new_points_list.insert(0, (counter + 1, data[0], data[1], data[2]))
                insert_done = True
            else:
                if insert_done:
                    new_points_list.insert(0, best_individual_games[counter-1])
                else:
                    new_points_list.insert(0, [best_individual_games[counter-1][0] + 1, best_individual_games[counter-1][1],best_individual_games[counter-1][2], best_individual_games[counter-1][3]])
                    
                counter -= 1
                pointer += 1
    else:
        new_points_list = best_individual_games
    
    # Prepare dictionary to write as jason
    to_write = {}
    to_write['best_individual_games'] = new_points_list
    
    # Store to file
    with open('data/scoreboard_individual.json', 'w') as outfile:
        json.dump(to_write, outfile,  sort_keys=True, indent=4)
        
    return

def insert_in_scoreboard_all_games(data):
    global best_all_games

    # Get list of points from json - already sorted
    sorted_points = [] #Reverse order
    for item in best_all_games:
        sorted_points.insert(0, item[2])
    
    # Add new points - only if it is more than at least the smallest number 
    if data[1] > min(sorted_points):
        sorted_points.insert(0, data[1])
        sorted_points.sort()
        
        # Reduce length of list to 10 so that I will have the best 10 
        # when I insert the new data
        while len(sorted_points) > 10:
            del sorted_points[0]

        # Build new list of sorted data
        insert_done = False
        
        new_points_list =[]
        counter = len(best_all_games)-1
        pointer = 0
        
        for item in sorted_points:
            if item == data[1] and insert_done == False: # New item
                new_points_list.insert(0, (counter + 1, data[0], data[1], data[2]))
                insert_done = True
            else:
                if insert_done:
                    new_points_list.insert(0, best_all_games[counter-1])
                else:
                    new_points_list.insert(0, [best_all_games[counter-1][0] + 1, best_all_games[counter-1][1],best_all_games[counter-1][2],best_all_games[counter-1][3]])
                    
                counter -= 1
                pointer += 1
    else:
        new_points_list = best_all_games
    
    # Prepare dictionary to write as jason
    to_write = {}
    to_write['best_all_games'] = new_points_list

    # Store to file  
    with open('data/scoreboard_all_games.json', 'w') as outfile:
        json.dump(to_write, outfile,  sort_keys=True, indent=4)

    return


@app.route('/', methods=['GET','POST'])
def index():
    global app_info
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
    app_info["route"] = "index"
    return render_template("index.html", login_feedback=login_feedback)
    

@app.route('/about')
def about():
    global app_info
    app_info["route"] = "about"
    return render_template("about.html", app_info=app_info)


@app.route('/contact', methods=['GET','POST'])
def contact():
    global app_info
    app_info["route"] = "contact"
    return render_template("contact.html", app_info=app_info)
    

@app.route('/scoreboard')
def scoreboard():
    global app_info
    app_info["route"] = "scoreboard"
    return render_template("scoreboard.html", app_info=app_info)
    
@app.route('/register', methods=['GET','POST'])
def register():
    global app_info
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
    global app_info
    global user_data
    global current_game
    global current_riddle
    global all_riddles
    global riddle_counter
    global gained_points
    global attempt
    
    user_data_json = json.loads(read_from_file("user_game_data_json.json"), object_hook=json_tuple_helper_function)
    
    user_data = find_loggedin_user(user_data_json)
    
    if app_info["game"] == False:  # RESET
        current_game = []
        current_riddle = 0
        all_riddles = []
        riddle_counter = 0
        
    fill_best_individual_games()
    fill_best_all_games()
        
    app_info["route"] = "user"
    username_feedback = app_info["username"].capitalize()
    return render_template("user.html", username_feedback=username_feedback, app_info=app_info, user_data=user_data, attempt=attempt, gained_points=gained_points)

@app.route('/game', methods=['GET', 'POST'])
def game():
    global app_info
    global all_riddles
    global current_game
    global current_riddle
    global riddle_counter
    global attempt
    global points
    global gained_points
    global wrong_answers
    global answer
    
    if app_info["game"] == False:
        app_info["game"] = True  # Game On
        all_riddles = json.loads(read_from_file("riddles.json"))
        
    for x in range(0, 10):  # Select 10 images at random
            repeat = True
            while repeat:
                choose_game=random.choice(all_riddles)
                if choose_game.items() not in current_game:
                    repeat = False
            current_game.append(choose_game.items())
        
            current_riddle = sort_current_riddle(current_game[riddle_counter])
            
    if request.method == 'POST':
        if 'play' in request.form:
            points = 9
            attempt = 1
            
        elif 'answer_btn' in request.form:
            # Check Answer
            if attempt == 1:
                answer = request.form['answer_text']
                
                # Clean the answer
                # If there are multiple spaces or other white characters in between the words
                temp =[]                    # Clean answer
                temp = answer.split()
                answer=""
                for item in temp:
                    answer += item + " "
                    
                answer = answer.strip()         # Strip trailing spaces
                
                if answer.lower() == current_riddle[2].lower(): # answer correct
                    gained_points += 9
                    wrong_answers = []
                    attempt = 1                  # First attempt of
                    riddle_counter += 1         # Next Riddle
                    if riddle_counter > len(current_game)-1:    # If that was last riddle then
                        # store_game_info()
                        return redirect(url_for('game_over'))   # GAME OVER
                    # Trigger next riddle
                    current_riddle = sort_current_riddle(current_game[riddle_counter]) 
            
                else:                           # Otherwise answer is wrong
                    if len(answer) == 0:        #if no answer is given
                        wrong_answers.append("-")
                    else:
                        wrong_answers.append(answer)
                    attempt = 2                 # This is your next attempt
                    points = 6                  # Set correct number of points
        elif attempt == 2:
                
                # Get all words and concatenate them
                answer = ""
                index = ""
                local_answer = current_riddle[2].split()
                for ndx, each_word in enumerate(local_answer):
                    index = 'answer_text' + str(ndx+1)
                    answer += (request.form[index].strip() + " ") #Strip any typed white spaces
                    
                temp =[]                        # Clean answer
                temp = answer.split()
                answer=""
                for item in temp:
                    answer += item + " "
                answer = answer.strip()         # Strip trailing spaces
                
                if answer.lower() == current_riddle[2].lower(): # Answer correct
                    gained_points += 6          # Gain points
                    attempt = 1                 # Reset attempt
                    points = 9
                    wrong_answers = []

                    riddle_counter += 1
                    if riddle_counter > len(current_game)-1:
                        # store_game_info()
                        return redirect(url_for('game_over'))

                    current_riddle = sort_current_riddle(current_game[riddle_counter])
                
                else:                           # Otherwise answer is wrong
                    # wrong_answers.append(answer)
                    if len(answer) == 0:                #if no answer is given
                        wrong_answers.append("-")
                    else:
                        wrong_answers.append(answer)
                    attempt = 3                 # This is your next attempt
                    points = 3                  # Set correct number of points
                
        elif attempt == 3:
                answer = ""
                index = ""
                local_answer = current_riddle[2].split()
                
                for ndx, each_word in enumerate(local_answer):
                    index = 'answer_text' + str(ndx+1)
                    answer += (request.form[index].strip() + " ") #Strip any typed white spaces
                    
                # answer = answer[0:-1]      # Strip final space
                temp =[]                    # Clean answer
                temp = answer.split()
                answer=""
                for item in temp:
                    answer += item + " "
                answer = answer.strip()         # Strip trailing spaces
                
                if answer.lower() == current_riddle[2].lower():  # Answer correct
                    gained_points += 3           # Gain points
                    attempt = 1                  # Reset attempt
                    points = 9
                    wrong_answers = []           # Reset wrong answers

                    riddle_counter += 1
                    if riddle_counter > len(current_game)-1:
                        # store_game_info()
                        return redirect(url_for('game_over'))

                    current_riddle = sort_current_riddle(current_game[riddle_counter])
                
                # Otherwise answer is wrong
                else:
                    attempt = 1                 # This is your next attempt
                    points = 9                # Set correct number of points
                    wrong_answers = []           # Reset wrong answers
                    riddle_counter += 1
                    if riddle_counter > len(current_game)-1:
                        # store_game_info()
                        return redirect(url_for('game_over'))
                    current_riddle = sort_current_riddle(current_game[riddle_counter])
                    
        elif 'pass_btn' in request.form:
            if attempt == 1:
                wrong_answers = []
                wrong_answers = ["-"]
                attempt = 2
                points = 6
            elif attempt == 2:
                points = 3
                wrong_answers.append("-")
                attempt = 3
            elif attempt == 3:
                if riddle_counter > len(current_game)-1:
                    # store_game_info()
                    return redirect(url_for('game_over'))
                current_riddle = sort_current_riddle(current_game[riddle_counter])
                points = 9
                attempt = 1
                riddle_counter += 1
                wrong_answers = []
                
                if riddle_counter > len(current_game)-1:     # Call next riddle
                    return redirect(url_for('game_over'))
                current_riddle = sort_current_riddle(current_game[riddle_counter])
                
    return render_template("game.html", app_info=app_info, all_riddles=all_riddles, current_game=current_game, current_riddle=current_riddle, riddle_counter=riddle_counter+1, attempt=attempt, points=points, gained_points=gained_points, wrong_answers=wrong_answers)

@app.route('/game_over')
def game_over():
    global app_info
    global gained_points
    global attempt
    global user_data
    app_info["route"] = "game"
    app_info["game"] = False
    flash(gained_points)
    store_game_info()  # Updates Hall of fame too
    global_game_reset()
    app_info["route"] = "user"
    return render_template("user.html", app_info=app_info, user_data=user_data, attempt=attempt, gained_points=gained_points)
                

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)