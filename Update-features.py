# FLASK Tutorial 1 -- We show the bare bones code to get an app up and running

# imports
import os  # os is used to get environment variables IP & PORT

import bcrypt
from flask import Flask  # Flask is the web app that we will customize
from flask import render_template, flash
from flask import request
from flask import redirect, url_for
from database import db
from models import Question as Question
from models import User as User
from forms import RegisterForm
from flask import session, send_from_directory, send_file
from forms import LoginForm
from models import Comment as Comment
from forms import RegisterForm, LoginForm, CommentForm, SearchForm, UpdateAccountForm
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads/'


app = Flask(__name__)  # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_QA_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'SE3155'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Bind SQLAlchemy db object to this Flask app
db.init_app(app)
# Set up models
with app.app_context():
    db.create_all()
# notes = {1: {'title': 'First note', 'text': 'This is my first note', 'date': '10-1-2020'},
#         2: {'title': 'Second note', 'text': 'This is my second note', 'date': '10-2-2020'},
#        3: {'title': 'Third note', 'text': 'This is my third note', 'date': '10-3-2020'}}

# UPLOAD_FOLDER = 'static/uploads'

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if session.get('user'):
        # search = SearchForm(request.form)
        # if request.method == 'POST':
        # return search_results(search)

        return render_template('index.html', user=session['user'])
    # return render_template("index.html", user=session['user']
    else:
        return render_template("index.html")


@app.route('/questions')
def get_questions():
    if session.get('user'):
        q = request.args.get('q')
        if q:
            my_questions = db.session.query(Question).filter_by(user_id=session['user_id']).filter(
                Question.title.contains(q) | Question.text.contains(q))
        else:
            my_questions = db.session.query(Question).filter_by(user_id=session['user_id']).all()
        return render_template('notes.html', questions=my_questions, user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/questions/<question_id>')
def get_question(question_id):
    if session.get('user'):

        my_question = db.session.query(Question).filter_by(id=question_id, user_id=session['user_id']).one()
        form = CommentForm()
        return render_template('note.html', question=my_question, user=session['user'], form=form)
    else:
        return redirect(url_for('login'))


@app.route('/questions/new', methods=['GET', 'POST'])
def new_question():
    if session.get('user'):
        # check method used for request
        print('request method is ', request.method)
        if request.method == 'POST':
            # get title data
            title = request.form['title']
            # get note data
            text = request.form['questionText']
            # create date stamp
            from datetime import date
            today = date.today()
            # fromat date mm/dd/yyyy
            today = today.strftime("%m-%d-%y")
            # get the last ID used and increment by 1
            new_record = Question(title, text, today, session['user_id'])
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for('get_questions'))
        else:
            return render_template('new.html', user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/questions/edit/<question_id>', methods=['GET', 'POST'])
def update_question(question_id):
    if session.get('user'):
        if request.method == 'POST':
            title = request.form['title']
            text = request.form['questionText']
            question = db.session.query(Question).filter_by(id=question_id).one()

            question.title = title
            question.text = text

            db.session.add(question)
            db.session.commit()

            return redirect(url_for('get_questions'))
        else:

            my_question = db.session.query(Question).filter_by(id=question_id).one()

            return render_template('new.html', question=my_question, user=session['user'])
    else:
        return redirect(url_for('login'))


@app.route('/questions/delete/<question_id>', methods=['POST'])
def delete_question(question_id):
    if session.get('user'):
        my_question = db.session.query(Question).filter_by(id=question_id).one()
        db.session.delete(my_question)
        db.session.commit()

        return redirect(url_for('get_questions'))
    else:
        return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for('get_questions'))

    # something went wrong - display register view
    return render_template('register.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('get_questions'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    # check if a user is saved in session
    if session.get('user'):
        session.clear()

    return redirect(url_for('index'))


@app.route('/questions/<question_id>/comment', methods=['POST'])
def new_comment(question_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(question_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_question', question_id=question_id))

    else:
        return redirect(url_for('login'))


@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search.data['search'] == '':
        qry = db.session.query(Question)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        return render_template('notes.html', results=results)


@app.route('/questions/upload')
def upload_form():
    return render_template('upload.html')


@app.route('/questions/upload', methods=['GET','POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('upload_image'))
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(url_for('upload_image'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        return render_template('upload.html', filename=filename)
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(url_for('upload_image'))


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/uploads/<filename>', methods = ["GET", "POST"])
def download(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')

#@app.route('/user_account', methods=['POST', 'GET'])
def account_settings():
    form = UpdateAccountForm()
    image_file = url_for('static', filename=('profile_pic/') + 'avatar.png')

    if request.method == 'POST' and form.validate_on_submit():
        h_password = bcrypt.hashpw(
            request.form['new_password'].encode('utf-8'), bcrypt.gensalt())
        new_email = request.form['email']
        user = session.get('user')
        #update_user = User(user.first_name, user.last_name, new_email, h_password)
        #User.email(new_email)
        #db.session.add(update_user)
        db.session.commit()
        return(url_for('account_settings'))

    return render_template("account.html", image_file=image_file, form=form, user=session['user'])


app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)), debug=True)

# To see the web page in your web browser, go to the url,
# http://127.0.0.1:5000

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.
