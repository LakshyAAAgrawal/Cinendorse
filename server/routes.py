from flask import render_template
from server import app
from flask import request
from server.forms import LoginForm
from server.movie_rec import *
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
      result = request.form
      recomm=recommendations_user(10, result['username'])
      if(recomm==None):
          return('No such user')
      else:
          return(str(recomm))
