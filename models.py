from database import db
import datetime

class Question(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship("Comment", backref="question", cascade="all, delete-orphan", lazy = True)
    def __init__(self, title, text, date, user_id):
        self.title = title
        self.text = text
        self.date = date
        self.user_id = user_id

class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    questions = db.relationship("Question", backref="user", lazy=True)
    comments = db.relationship("Comment", backref = "user", lazy=True)
    #liked = db.relationship('PostLike', foreign_keys = 'PostLike.user_id', backref = 'user', lazy = 'dynamic')

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = datetime.date.today()

    #def like_post(self, question):
        #if not self.has_liked_post(question):
            #like = PostLike(user_id = self.id, question_id = question.id)
            #db.session.add(like)

    #def unlike_post(self, question):
        #if self.has_liked_post(question):
            #PostLike.query.filter_by(
                #user_id = self.id,
                #question_id = self.id).delete()

    #def has_liked_post(self, question):
        #return PostLike.query.filter(
            #PostLike.user_id == self.id,
            #PostLike.question_id == question.id).count()>0

#class PostLike(db.Model):
    #id = db.Column(db.Integer, primary_key = True)
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #question_id = db.Column(db.Integer, db.ForeignKey('question_.id'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.VARCHAR, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, content, question_id, user_id):
        self.date_posted = datetime.date.today()
        self.content = content
        self.question_id = question_id
        self.user_id = user_id
