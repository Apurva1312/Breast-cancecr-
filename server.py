from flask import Flask,render_template,request, url_for
from datetime import datetime
from flask_cors import CORS, cross_origin
import pickle
import numpy as np
import pandas as pd
import sqlite3 as sq
import time


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

model = pickle.load(open('breast_cancer_detector.pickle', 'rb'))


@app.route('/')
@cross_origin()
def home():
    return render_template('index.html')

@app.route('/test')
@cross_origin()
def render_test():
    return render_template('test.html')


@app.route('/predict',methods=['POST'])
@cross_origin()
def predict():
    input_features = [float(x) for x in request.form.values()]
    features_value = [np.array(input_features)]
    
    features_name = ['mean radius', 'mean texture', 'mean perimeter', 'mean area',
       'mean smoothness', 'mean compactness', 'mean concavity',
       'mean concave points', 'mean symmetry', 'mean fractal dimension',
       'radius error', 'texture error', 'perimeter error', 'area error',
       'smoothness error', 'compactness error', 'concavity error',
       'concave points error', 'symmetry error', 'fractal dimension error',
       'worst radius', 'worst texture', 'worst perimeter', 'worst area',
       'worst smoothness', 'worst compactness', 'worst concavity',
       'worst concave points', 'worst symmetry', 'worst fractal dimension']
    
    df = pd.DataFrame(features_value, columns=features_name)
    output = model.predict(df)
        
    if output == 0:
        res_val = "** breast cancer **"
    else:
        res_val = "no breast cancer"
        
    print(res_val)
    return render_template('test.html', prediction_text='Patient has {}'.format(res_val))


# login and register routes

#-- Database section using Sqlite for data handling
#-- Create function creates a connection file if doesn't exists
def create():
    db = sq.connect("site_db")
    cursor = db.cursor()
    print("creating database connection file!")
    time.sleep(1)
    cursor.execute(""" CREATE TABLE IF NOT EXISTS users(name TEXT, email TEXT, password BLOB) """)
    db.commit()

#-- Insert function add new record to database
def insert(name, email, password):
    db = sq.connect("site_db")
    cursor = db.cursor()
    cursor.execute("""INSERT INTO users (name, email, password) VALUES(?,?,?)""",(name,email,password))
    db.commit()
    db.close()

#-- basic data check, using email address to check if user already registred or not
def check_data(email):
    db = sq.connect("site_db")
    cursor = db.cursor()
    cursor.execute("""SELECT email FROM users WHERE email=(?)""",(email,))
    data = cursor.fetchall()
    if len(data) == 0:
        return True

#-- Basic data check, using email and password to check if user entred correct login info
def check_login_data(email, password):
    db = sq.connect("site_db")
    cursor = db.cursor()
    cursor.execute("""SELECT email FROM users WHERE email=(?)""",(email,))
    data = cursor.fetchall()
    print(data)
    if len(data) > 0:
        cursor.execute("""SELECT password FROM users WHERE password=(?)""",(password,))
        data = cursor.fetchall()
        print(data)
        if len(data) > 0:
            return True

#-- calling the create function each time
create()


@app.route('/register')
@cross_origin()
def register():
    return render_template('Login-Page.html')

#-- mapping for register_success page
#-- the registery page uses post method to send data to server
@app.route("/register_success", methods = ["POST"])
def register_success():
    #-- checking for method and runing data check before sending data to
    #-- Sqlite
    if request.method == "POST":
        email = request.form["email"]
        if check_data(email):
            email = request.form["email"]
            name = request.form["name"]
            password = request.form["password"]
            print(name)
            print(email)
            print(password)
            insert(name, email, password)
            return render_test()
        else:
            return home()

#-- same as register_success page here we use POST method to send data
#-- back to server, so we can run data check for login proccess
@app.route("/login_success", methods = ["POST"])
def login_success():
    #-- using email and password
    #-- first check if even email exists if yes checks for password
    #-- we can expand system by creating auto send reset link to user Email
    #-- in a case that they forgot their password
    if request.method == "POST":
        email = request.form["email"]
        print(email)
        password = request.form["password"]
        print(password)
        if check_login_data(email, password):
            return render_test()
        else:
            return home()

if __name__ =='__main__':
    app.run(debug=True)