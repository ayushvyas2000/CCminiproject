from flask import Flask, request, render_template,session,redirect,url_for
import numpy as np
import pickle
import string 
import bz2
from flask_sqlalchemy import SQLAlchemy

def preprocess(text):   
    preprocessed_text = text.lower().replace('-', ' ')
    
    translation_table = str.maketrans('\n', ' ', string.punctuation+string.digits)
    
    preprocessed_text = preprocessed_text.translate(translation_table)
        
    return preprocessed_text

app2 = Flask(__name__)
model = pickle.load(open('random_forest_regression_model.pkl', 'rb'))
app2.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mikrbmumflodur:feefbda53896a44440ddbff42ecee8052bca8929e22e0e3f606027f99754a9c0@ec2-34-202-54-225.compute-1.amazonaws.com:5432/dbrtjs3dtdmtgl'
app2.config['SECRET_KEY'] = "Ayush"

db = SQLAlchemy(app2)

class User(db.Model):
   __tablename__ = 'User'
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(100))
   password = db.Column(db.String(50))

   def __init__(self, name, password):
       self.name = name
       self.password = password
    
db.create_all()
db.session.commit()

@app2.route('/')
@app2.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        name = request.form['name']
        password = request.form['password']
        data = User.query.filter_by(name=name, password=password).first()
        if data:
            session['loggedin'] = True
            session['id'] = data.id
            session['name'] = data.name
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect name / password !'
    return render_template('login.html', msg = msg)

@app2.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

@app2.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form :
        name = request.form['name']
        password = request.form['password']
        new_user = User(name = name,password = password)
        if db.session.query(User).filter(User.name == name).count():
            msg = 'Account already exists !'
        elif not name or not password:
            msg = 'Please fill out the form !'
        else:
            db.session.add(new_user)
            db.session.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)


@app2.route('/predict',methods=['POST'])
def predict():
    Fuel_Type_Diesel=0
    if request.method == 'POST':
        Year = int(request.form['Year'])
        Present_Price=float(request.form['Present_Price'])
        Kms_Driven=int(request.form['Kms_Driven'])
        Kms_Driven2=np.log(Kms_Driven)
        Owner=int(request.form['Owner'])
        Fuel_Type_Petrol=request.form['Fuel_Type_Petrol']
        if(Fuel_Type_Petrol=='Petrol'):
                Fuel_Type_Petrol=1
                Fuel_Type_Diesel=0
        else:
            Fuel_Type_Petrol=0
            Fuel_Type_Diesel=1
        Year=2020-Year
        Seller_Type_Individual=request.form['Seller_Type_Individual']
        if(Seller_Type_Individual=='Individual'):
            Seller_Type_Individual=1
        else:
            Seller_Type_Individual=0	
        Transmission_Mannual=request.form['Transmission_Mannual']
        if(Transmission_Mannual=='Mannual'):
            Transmission_Mannual=1
        else:
            Transmission_Mannual=0
        prediction=model.predict([[Present_Price,Kms_Driven2,Owner,Year,Fuel_Type_Diesel,Fuel_Type_Petrol,Seller_Type_Individual,Transmission_Mannual]])
        output=round(prediction[0],2)
        if output<0:
            return render_template('index.html',prediction_texts="Sorry you cannot sell this car")
        else:
            return render_template('index.html',prediction_text="You Can Sell The Car at {} lakhs".format(output))
    else:
        return render_template('index.html')
    

if __name__ == "__main__":
    app2.run(debug=True)
