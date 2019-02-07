from flask import render_template
from server import app
from flask import request
from server.forms import LoginForm
from Recommendation.movie_rec import *
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
      result = request.form
      recomm=recommendations_user(10, result['username'])
      to_pass=recom_parse(recomm)
      rand_mov=random_movies(10)
      if(recomm==None):
          return('No such user')
      else:
          return render_template('recom_display.html', result=to_pass, random_movies=rand_mov)
    else:
        return('Not Supported')


@app.route('/ratings', methods = ['POST', 'GET'])
def ratings():
    if request.method == 'POST':
      result = request.form
      return(str(result))
    else:
        return('Not Supported')
