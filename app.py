from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
from models import User
import users_dao, quest_sessions_dao, enrollments_dao, quests_dao


app = Flask(__name__)
app.config["SECRET_KEY"] = "TheMysticGroveKey" #serve criptografare i cookie

login_manager = LoginManager()
login_manager.init_app(app)


#Lists and dictionary for validation
SIMULATED_CURRENT_TIME = {
    "day": "wednesday",
    "time": "14:00"
}

VALID_ROLES = ['warrior', 'mage', 'healer']

VALID_LOCATIONS = ["Whispering Hollow", "Moonlit Wood", "Mystic Tower"]

VALID_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

DAY_TO_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6
}

#Support functions 
def day_time_to_minutes(day, time):
    day_index = DAY_TO_INDEX[day]
    parts = time.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])

    return day_index * 24 * 60 + hours *60 + minutes


def sessions_overlap(day_a, start_a, duration_a, day_b, start_b, duration_b):
    start_a_min = day_time_to_minutes(day_a, start_a)
    end_a_min = start_a_min + duration_a

    start_b_min = day_time_to_minutes(day_b, start_b)
    end_b_min = start_b_min + duration_b

    if start_a_min < end_b_min and start_b_min < end_a_min:
        return True
    return False


#login/signup routes

@login_manager.user_loader
def load_user(user_id):
    db_user = users_dao.get_user_by_id(user_id)
    if db_user is not None:
        user = User(
            id=db_user["id"],
            username=db_user["username"],
            email=db_user["email"],
            password=db_user["password"],
            role=db_user["role"],
        )
    else:
        user = None
    return user


@app.route("/signup")
def signup():
    return render_template("registration.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("txt_username")
    email = request.form.get("txt_email")
    password = request.form.get("txt_password")

    if not username or not email or not password:
        flash("Please fill all fields.", "warning")
        return redirect(url_for("signup"))

    existing_user = users_dao.get_user_by_email(email)
    if existing_user:
        flash("Email already registered.", "danger")
        return redirect(url_for("signup"))

    hashed_password = generate_password_hash(password)
    users_dao.new_user(username, email, hashed_password, "adventurer")

    flash("Registration successful! You can now log in.", "success")
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")



@app.route("/authenticate", methods=["POST"])
def authenticate():
    form_user = request.form.to_dict()

    db_user = users_dao.get_user_by_email(form_user["txt_email"])

    if not db_user:
        flash("The user does not exist", "danger")
        return redirect(url_for("home"))
    
    
    elif not check_password_hash(db_user["password"], form_user["txt_password"]):
        flash("The user does not exist", "danger")
        return redirect(url_for("home"))
    
    else:
        new = User(
            id = db_user["id"],
            username = db_user["username"],
            email = db_user["email"],
            password= db_user["password"],
            role = db_user["role"],
        )

        login_user(new)
        flash("Welcome back! " + db_user["username"], "success")
    
    return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


#home route


@app.route('/')
def home():   
    filter_day = request.args.get('day', 'all')
    filter_type = request.args.get('type', 'all')
    filter_difficulty = request.args.get('difficulty', 'all')
    filter_role = request.args.get('role', 'all')

    db_sessions = quest_sessions_dao.get_all_sessions()

    sessions_filtered = []

    for s in db_sessions:
        if filter_day != 'all' and s['day'] != filter_day:
            continue
        if filter_type != 'all' and s['quest_type'] != filter_type:
            continue
        if filter_difficulty != 'all' and s['difficulty'] != filter_difficulty:
            continue

        db_taken_places = enrollments_dao.get_places_taken(s['id'])

        free_places = {}

        free_places['warrior'] = 4 - db_taken_places['warrior']
        free_places['mage'] = 3 - db_taken_places['mage']
        free_places['healer'] = 2 - db_taken_places['healer']

        if filter_role != 'all' and free_places[filter_role] <= 0:
            continue

        session_data = dict(s)
        session_data['free_places'] = free_places
        sessions_filtered.append(session_data)

    days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    sessions_order_by_day = {}

    for d in days_order:
        sessions_order_by_day[d] = []          
        for session in sessions_filtered:
            if session['day'] == d:
                sessions_order_by_day[d].append(session)

    return render_template('index.html', sessions_order_by_day=sessions_order_by_day)


#quest details route and enrollments manager

@app.route("/session_details/<int:session_id>")
def quest_session(session_id):

    db_session = quest_sessions_dao.get_sessions_by_id(session_id)  
    if db_session is None:
        flash("Session not found.", "danger")
        return redirect(url_for('home'))
 
    return render_template("quest.html", session=db_session)


@app.route('/enroll/<int:session_id>', methods=['POST'])
@login_required
def enroll(session_id):
    if current_user.role != 'adventurer':
        flash("Only adventurers can enroll in a session", "danger")
        return redirect(url_for('quest_session', session_id=session_id))
    
    chosen_role = request.form.get('role')

    if chosen_role not in VALID_ROLES:
        flash("Invalid role.", "danger")
        return redirect(url_for('quest_session', session_id=session_id))

    reserved_places = request.form.get('number')

    if not chosen_role or not reserved_places:
        flash("Please, chose a class and the number of places to reserve", "warning")
        return redirect(url_for('quest_session', session_id = session_id))
    
    try:
        reserved_places = int(reserved_places)
    except ValueError:
        flash("Placeses reserved must be a number.", "danger")
        return redirect(url_for('quest_session', session_id = session_id))


    if reserved_places < 1 or reserved_places > 2:
        flash("Book 1 or 2 places.", "danger")
        return redirect(url_for('quest_session', session_id=session_id))
       

    db_session = quest_sessions_dao.get_sessions_by_id(session_id)

    if db_session is None:
        flash("Session not found.", "danger")
        return redirect(url_for('home'))


    current_minutes = day_time_to_minutes(SIMULATED_CURRENT_TIME['day'], SIMULATED_CURRENT_TIME['time'])
    session_minutes = day_time_to_minutes(db_session['day'], db_session['start_time'])
    
    if session_minutes <= current_minutes:
        flash("This session has already started. You cannot enroll anymore.", "danger")
        return redirect(url_for('quest_session', session_id=session_id))

    taken = enrollments_dao.get_places_taken(session_id)
    max_places = {'warrior': 4, 'mage': 3, 'healer': 2}
    free_places = max_places[chosen_role] - taken[chosen_role]

    if reserved_places > free_places:
        flash(f"Not enough places avaible: only {free_places} for {chosen_role}.", "danger")
        return redirect(url_for('quest_session', session_id = session_id))

    user_currente_session_enrollments = enrollments_dao.get_enrollment_for_user_session(current_user.id, session_id)
    
    if user_currente_session_enrollments is not None:
        flash("You already enrolled to this section.", "warning")
        return redirect(url_for('quest_session', session_id=session_id))

    user_enrollments = enrollments_dao.get_enrollments_by_user(current_user.id)

    if len(user_enrollments) >=3:
        flash("Limit reached: you already enrolled to 3 session for this week","danger" )
        return redirect(url_for('quest_session', session_id=session_id))

    for e in user_enrollments:
        overlap = sessions_overlap(
            db_session['day'], db_session['start_time'], db_session['duration_min'],
            e['day'], e['start_time'], e['duration_min']
        )
        if overlap:
            flash("You already have a booked session for this time.", "danger")
            return redirect(url_for('quest_session', session_id=session_id))

    enrollments_dao.new_enrollment(current_user.id, session_id, chosen_role, reserved_places)
    flash("You enrolled to the session successfully", "success")
    return redirect(url_for("home"))


#guild master
@app.route("/profile_guild_master")
@login_required
def profile_master():
    if current_user.role != 'guild_master':
        flash("You are not allowed to perform this action.", "danger")
        return redirect(url_for('home'))
    all_quests = quests_dao.get_all_quests()

    quests_with_sessions = []

    for q in all_quests:
        sessions = quest_sessions_dao.get_sessions_by_quest_id(q['id'])
        sessions_with_places = []
        for s in sessions:
            taken = enrollments_dao.get_places_taken(s['id'])

            session_data = dict(s)
            session_data['taken_places'] = taken
            sessions_with_places.append(session_data)

            most_requested = "warrior"
            for ruolo in taken:
                if taken[ruolo] > taken[most_requested]:
                    most_requested = ruolo
            
            session_data['most_requested_role'] = most_requested

        quest_data = dict(q)
        quest_data['sessions'] = sessions_with_places
        quests_with_sessions.append(quest_data)

    return render_template('profile_guild_master.html', quests=quests_with_sessions)


@app.route("/create_new_quest", methods=['POST'])
@login_required
def create_new_quest():
    if current_user.role != 'guild_master':
        flash("You are not allowed to perform this action.", "danger")
        return redirect(url_for('home'))
     
    title = request.form.get("txt_title")
    duration = request.form.get("txt_duration")
    difficulty = request.form.get("txt_difficulty")
    quest_type = request.form.get('txt_type')
    description = request.form.get('txt_description')
    image_file = request.files.get('quest_img')

    if not title or not duration or not difficulty or not quest_type or not description or not image_file or image_file.filename == "":
        flash("Please fill all the required fields.", "warning")
        return redirect(url_for("profile_master"))
    
    if len(title) < 3 or len(title) > 50:
        flash("Title must be between 3 and 50 characters.", "danger")
        return redirect(url_for('profile_master'))
    
    if len(description) < 10 or len(description) > 500:
        flash("Description must be between 10 and 500 characters.", "danger")
        return redirect(url_for('profile_master'))
    
    try:
        duration = int(duration)
    except ValueError:
        flash("Duration must be a number.", "danger")
        return redirect(url_for('profile_master'))

    if duration < 1 or duration > 600:
        flash("Duration must be between 1 and 600 minutes.", "danger")
        return redirect(url_for('profile_master'))

    valid_difficulties = ["easy", "medium", "hard", "legendary"]
    valid_types = ["combat", "exploration", "puzzle", "stealth", "magic", "survival"]

    if difficulty not in valid_difficulties:
        flash("Invalid difficulty.", "danger")
        return redirect(url_for('profile_master'))

    if quest_type not in valid_types:
        flash("Invalid quest type.", "danger")
        return redirect(url_for('profile_master'))
    
    secs = int(datetime.now().timestamp())
    ext = image_file.filename.split(".")[-1]
    img_name = str(secs) + "." + ext

    
    image_file.save("static/images/quest_imgs/" + img_name)

    quests_dao.new_quest(title, duration, quest_type, difficulty, description, "images/quest_imgs/" + img_name)

    flash("Quest created successfully!", "success")
    return redirect(url_for('profile_master'))


@app.route('/schedule_new_session', methods=['POST'])
@login_required
def schedule_new_session():
    if current_user.role != 'guild_master':
        flash("You are not allowed to perform this action.", "danger")
        return redirect(url_for('home'))
    
    quest_id = request.form.get('txt_quest_id')
    day = request.form.get('txt_day')
    start_time = request.form.get('start_time')
    location = request.form.get('location')

    if not quest_id or not day or not start_time or not location:
        flash("Please fill in all the required fields.", "warning")
        return redirect(url_for('profile_master'))

    if day not in VALID_DAYS:
        flash("Invalid day.", "danger")
        return redirect(url_for('profile_master'))

    if location not in VALID_LOCATIONS:
        flash("Invalid location.", "danger")
        return redirect(url_for('profile_master'))

    quest = quests_dao.get_quest_by_id(quest_id)
    if not quest:
        flash("Selected quest does not exist.", "danger")
        return redirect(url_for('profile_master'))

    new_session_duration = quest['duration_min']

    current_minutes = day_time_to_minutes(SIMULATED_CURRENT_TIME['day'], SIMULATED_CURRENT_TIME['time'])
    new_session_minutes = day_time_to_minutes(day, start_time)

    if new_session_minutes <= current_minutes:
        flash("You cannot schedule a session in the past.", "danger")
        return redirect(url_for('profile_master'))


    existing_sessions_same_location = quest_sessions_dao.get_sessions_by_location(location)

    for existing in existing_sessions_same_location:
        existing_quest = quests_dao.get_quest_by_id(existing['quest_id'])

        overlap = sessions_overlap(
            day, start_time, new_session_duration,
            existing['day'], existing['start_time'], existing_quest['duration_min']
        )

        if overlap:
            flash("This location is already booked for an overlapping time slot.", "danger")
            return redirect(url_for('profile_master'))

    quest_sessions_dao.new_session(quest_id, day, start_time, location)

    flash("Session scheduled successfully!", "success")
    return redirect(url_for('profile_master'))

@app.route('/edit_session/<int:session_id>', methods=['POST'])
@login_required
def edit_session(session_id):
    if current_user.role != 'guild_master':
        flash("You are not allowed to perform this action.", "danger")
        return redirect(url_for('home'))
    
    day = request.form.get('day')
    start_time = request.form.get('start_time')
    location = request.form.get('location')

    if not day or not start_time or not location:
        flash("Please fill in all the required fields.", "warning")
        return redirect(url_for('profile_master'))

    if day not in VALID_DAYS:
        flash("Invalid day.", "danger")
        return redirect(url_for('profile_master'))

    if location not in VALID_LOCATIONS:
        flash("Invalid location.", "danger")
        return redirect(url_for('profile_master'))

    session_to_edit = quest_sessions_dao.get_sessions_by_id(session_id)

    if not session_to_edit:
        flash("Session not found.", "danger")
        return redirect(url_for('profile_master'))

    taken = enrollments_dao.get_places_taken(session_id)
    total_enrolled = taken['warrior'] + taken['mage'] + taken['healer']

    if total_enrolled > 0:
        flash("This session cannot be modified because adventurers have already joined.", "danger")
        return redirect(url_for('profile_master'))

    quest = quests_dao.get_quest_by_id(session_to_edit['quest_id'])
    session_duration = quest['duration_min']

    current_minutes = day_time_to_minutes(SIMULATED_CURRENT_TIME['day'], SIMULATED_CURRENT_TIME['time'])
    new_session_minutes = day_time_to_minutes(day, start_time)

    if new_session_minutes <= current_minutes:
        flash("You cannot move a session to the past.", "danger")
        return redirect(url_for('profile_master'))


    existing_sessions_same_location = quest_sessions_dao.get_sessions_by_location(location)

    for existing in existing_sessions_same_location:

        if existing['id'] == session_id:
            continue

        existing_quest = quests_dao.get_quest_by_id(existing['quest_id'])

        overlap = sessions_overlap(
            day, start_time, session_duration,
            existing['day'], existing['start_time'], existing_quest['duration_min']
        )

        if overlap:
            flash("This location is already booked for an overlapping time slot.", "danger")
            return redirect(url_for('profile_master'))
  
    quest_sessions_dao.update_session(session_id, day, start_time, location)

    flash("Session updated successfully!", "success")
    return redirect(url_for('profile_master'))

@app.route('/delete_session/<int:session_id>', methods=['POST'])
@login_required
def delete_session(session_id):
    if current_user.role != 'guild_master':
        flash("You are not allowed to perform this action.", "danger")
        return redirect(url_for('home'))
    
    session_to_delete = quest_sessions_dao.get_sessions_by_id(session_id)

    
    if not session_to_delete:
        flash("Session not found.", "danger")
        return redirect(url_for('profile_master'))
    
    taken = enrollments_dao.get_places_taken(session_id)
    total_enrolled = taken['warrior'] + taken['mage'] + taken['healer']

    if total_enrolled > 0:
        flash("This session cannot be deleted because adventurers have already joined.", "danger")
        return redirect(url_for('profile_master'))
    
    quest_sessions_dao.delete_session(session_id)

    flash("Session deleted successfully!", "success")
    return redirect(url_for('profile_master'))
    

#adventurer profile

@app.route("/profile_user")
@login_required
def profile_user():
    if current_user.role != 'adventurer':
        flash("You are not allowed to perform this action.", "danger")
        return redirect(url_for('home'))

    db_enrollments = enrollments_dao.get_enrollments_by_user(current_user.id)

    current_minutes = day_time_to_minutes(SIMULATED_CURRENT_TIME['day'], SIMULATED_CURRENT_TIME['time'])
    
    enrollments_list = []
    
    for e in db_enrollments:
        e_dict = dict(e)
        
        taken = enrollments_dao.get_places_taken(e['session_id']) 
        e_dict['taken_places'] = {
            'warrior': taken['warrior'],
            'mage':  taken['mage'],
            'healer':  taken['healer']
        }
        
        session_minutes = day_time_to_minutes(e['day'], e['start_time'])
        time_diff = session_minutes - current_minutes
        
        e_dict['can_be_modified'] = (time_diff > 480)
            
        enrollments_list.append(e_dict)
    
    enrolled_count = len(enrollments_list)

    return render_template("profile_user.html", enrollments=enrollments_list, enrolled_count=enrolled_count)

@app.route('/edit_enrollment/<int:session_id>', methods=['POST'])
@login_required
def edit_enrollment(session_id):
    if current_user.role != 'adventurer':
        return redirect(url_for('home'))
    
    session_data = quest_sessions_dao.get_sessions_by_id(session_id) 

    if not session_data:
        flash("Session not found.", "danger")
        return redirect(url_for('profile_user'))

    
    current_minutes = day_time_to_minutes(SIMULATED_CURRENT_TIME['day'], SIMULATED_CURRENT_TIME['time'])
    session_minutes = day_time_to_minutes(session_data['day'], session_data['start_time'])
    
    if (session_minutes - current_minutes) <= 480:
        flash("Less than 8 hours remain before the quest starts.", "danger")
        return redirect(url_for('profile_user'))

    new_role = request.form.get('role')

    if new_role not in VALID_ROLES:
        flash("Invalid role.", "danger")
        return redirect(url_for('profile_user'))
    

    new_places = request.form.get('places')

    try:
        new_places = int(new_places)
    except (ValueError, TypeError):
        flash("Invalid number of places.", "danger")
        return redirect(url_for('profile_user'))


    if new_places < 1 or new_places > 2:
        flash("You can only reserve 1 or 2 places.", "danger")
        return redirect(url_for('profile_user'))

  
    current_enrollment = enrollments_dao.get_enrollment_for_user_session(current_user.id, session_id)

    if not current_enrollment or current_enrollment['user_id'] != current_user.id:
        flash("Enrollment not found.", "danger")
        return redirect(url_for('profile_user'))
    
    taken = enrollments_dao.get_places_taken(session_id)


    taken[current_enrollment['class']] -= current_enrollment['places']

    max_places = {'warrior': 4, 'mage': 3, 'healer': 2}
    free_places = max_places[new_role] - taken[new_role]

    if new_places > free_places:
        flash(f"Not enough places left! Only {free_places} places remain for {new_role.capitalize()}.", "danger")
        return redirect(url_for('profile_user'))

    enrollments_dao.update_enrollment(current_enrollment["id"], new_role, new_places)
    flash("Changes saved successfully!", "success")
    
    return redirect(url_for('profile_user'))


@app.route('/delete_enrollment/<int:session_id>/<int:id>', methods=['POST'])
@login_required
def delete_enrollment(session_id, id):
    if current_user.role != 'adventurer':
        return redirect(url_for('home'))
    
    enrollment = enrollments_dao.get_enrollment_by_id(id)

    if enrollment['session_id'] != session_id:         
        flash("Invalid request.", "danger")
        return redirect(url_for('profile_user'))

    if not enrollment or enrollment['user_id'] != current_user.id:
        flash("Enrollment not found.", "danger")
        return redirect(url_for('profile_user'))

    db_session = quest_sessions_dao.get_sessions_by_id(session_id)

    if not db_session:
        flash("Session not found", "danger")
        return redirect(url_for('profile_user'))

    
    current_minutes = day_time_to_minutes(SIMULATED_CURRENT_TIME['day'], SIMULATED_CURRENT_TIME['time'])
    session_minutes = day_time_to_minutes(db_session['day'], db_session['start_time'])
    
    if (session_minutes - current_minutes) <= 480:
        flash("Less than 8 hours remain before the quest starts", "danger")
        return redirect(url_for('profile_user'))
    
    enrollments_dao.delete_enrollment(id)
    flash("Enrollment cancelled successfully!", "success")
    return redirect(url_for('profile_user'))



#guild council administrator
@app.route('/profile_council')
@login_required
def profile_council():

    if current_user.role != 'guild_council':
        flash("access denied", "danger")
        return redirect(url_for('home'))

    all_adventurers = users_dao.get_all_adventurers()
    all_quests = quests_dao.get_all_quests()
    all_sessions = quest_sessions_dao.get_all_sessions()
    all_enrollments = enrollments_dao.get_all_enrollments()

    total_adventurers = len(all_adventurers)
    total_quests = len(all_quests)
    total_sessions = len(all_sessions)
    total_participations = len(all_enrollments)


    total_places_per_role = {'warrior': 0, 'mage': 0, 'healer': 0}
    for e in all_enrollments:
        total_places_per_role[e['class']] += e['places']



    most_popular = quests_dao.get_most_popular_quest_type()

    if most_popular is None:
        most_popular_type = "No enrollments yet"
    else:
        most_popular_type = most_popular['quest_type']

    busiest_sessions = [] 
    busiest_session_places = 0

    for s in all_sessions:
        taken = enrollments_dao.get_places_taken(s['id'])
        total_taken = taken['warrior'] + taken['mage'] + taken['healer']

        if total_taken > busiest_session_places:
            busiest_session_places = total_taken
            busiest_sessions = [dict(s)]
        elif total_taken == busiest_session_places and total_taken > 0:
            busiest_sessions.append(dict(s))

    adventurers_with_counts = []
    for a in all_adventurers:
        enrollments = enrollments_dao.get_enrollments_by_user(a['id'])
        a_dict = dict(a)
        a_dict['participation_count'] = len(enrollments)
        adventurers_with_counts.append(a_dict)


    quests_with_sessions = []
    for q in all_quests:
        sessions = quest_sessions_dao.get_sessions_by_quest_id(q['id'])
        sessions_with_places = []
        for s in sessions:
            taken = enrollments_dao.get_places_taken(s['id'])
            s_dict = dict(s)
            s_dict['taken_places'] = taken
            sessions_with_places.append(s_dict)

        q_dict = dict(q)
        q_dict['sessions'] = sessions_with_places
        quests_with_sessions.append(q_dict)


    stats = {
        'total_adventurers': total_adventurers,
        'total_quests': total_quests,
        'total_sessions': total_sessions,
        'total_participations': total_participations,
        'total_places_per_role': total_places_per_role,
        'most_popular_type': most_popular_type,
        'busiest_sessions': busiest_sessions,
        'busiest_session_places': busiest_session_places
    }

    return render_template(
        'profile_council.html',
        stats=stats,
        adventurers=adventurers_with_counts,
        quests=quests_with_sessions
    )

