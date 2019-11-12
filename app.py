from MySQLdb._mysql import connection
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
from flask_mysqldb import MySQL
#import mysql.connector
from wtforms import  Form, StringField, TextAreaField, validators, PasswordField, BooleanField
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc



app =Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='kroot'
app.config['MYSQL_PASSWORD']='1234'
app.config['MYSQL_DB']='flaskapp'
app.config['MYSQL_CURSORCLASS']= 'DictCursor'
#init
mysql= MySQL(app)

Articles = Articles()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email= StringField('Email', [validators.Length(min=6, max=50)])
    password= PasswordField('Password', [
    validators.DataRequired(),
    validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm= PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated November 11, 2019)', [validators.Required()])



@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            name= form.name.data
            username= form.username.data
            email= form.email.data
            password=sha256_crypt.encrypt(str(form.password.data))
            cur=mysql.connection.cursor()
            #cur.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))
            val = cur.execute("SELECT * FROM users WHERE username = (%s)",[thwart(username)])
            if int(val) >0:
                flash("That username is already taken, please choose another",'error')
                return render_template('register.html', form=form)

            else:
                cur.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)",(thwart(name), thwart(email), thwart(username), thwart(password)))


            mysql.connection.commit()
            flash("Thanks for registering!", 'success')
            cur.close()
            gc.collect()

            return redirect(url_for('index'))
        return render_template('register.html', form=form)
    except Exception as e:
        return(str(e))

if __name__ == '__main__':
    app.secret_key='mysecretpage'
    app.run(debug=True, host='0.0.0.0', port=81)
