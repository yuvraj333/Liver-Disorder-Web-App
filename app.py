import pickle

import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

#model = joblib.load('final_model.sav')

# Define the list of input field information here
input_fields = [
    {"id": "Age", "label": "Age", "placeholder": "Enter Age", "min": 0, "max": 100},
    {"id": "Gender", "label": "Gender", "placeholder": "Enter Gender", "min": 0, "max": 1},
    {"id": "Total_Bilirubin", "label": "Total Bilirubin", "placeholder": "Enter the Total Bilirubin", "min": 0, "max": 10},
    {"id": "Direct_Bilirubin", "label": "Direct Bilirubin", "placeholder": "Enter the Direct Bilirubin", "min": 0, "max": 10},
    {"id": "Alkaline_Phosphotase", "label": "Alkaline Phosphotase", "placeholder": "Enter the Alkaline Phosphotase", "min": 0, "max": 1000},
    {"id": "Alamine_Aminotransferase", "label": "Alamine Aminotransferase", "placeholder": "Enter the Alamine Aminotransferase", "min": 0, "max": 500},
    {"id": "Total_Protiens", "label": "Total Protiens", "placeholder": "Enter the Total Protiens", "min": 0, "max": 10},
    {"id": "Albumin", "label": "Albumin", "placeholder": "Enter the Albumin", "min": 0, "max": 10},
    {"id": "Albumin_and_Globulin_Ratio", "label": "Albumin and Globulin Ratio", "placeholder": "Enter the Albumin and Globulin Ratio", "min": 0, "max": 5},
]


app = Flask(__name__)


app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/help')
def help():
    return render_template("help.html")


@app.route('/terms')
def terms():
    return render_template("tc.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('liver'))

        return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")
    return render_template('signup.html', form=form)


#@app.route("/dashboard")
#@login_required
#def dashboard():
    #return render_template("dashboard.html")


@app.route("/disindex")

def disindex():
    return render_template("disindex.html")





@app.route("/liver")
@login_required
def liver():
    return render_template("liver.html")


def ValuePred(to_predict_list, size):
    to_predict = np.array(to_predict_list).reshape(1,size)
    if(size==9):
        loaded_model = joblib.load('liver_model.pkl')
        result = loaded_model.predict(to_predict)
    return result[0]


@app.route('/predictliver', methods=["POST"])
def predictliver():



    if request.method == "POST":
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        to_predict_list = list(map(float, to_predict_list))
        if len(to_predict_list) == 9:
            result = ValuePred(to_predict_list, 9)

    if int(result) == 1:
        prediction = "Patient has a high risk of Liver Disease, please consult your doctor immediately"
    else:
        prediction = "Patient has a low risk of Liver Disease"
    return render_template("liver_result.html", prediction_text=prediction)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))





############################################################################################################

if __name__ == "__main__":
    app.run(debug=True)

