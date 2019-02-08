from flask import render_template, redirect
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
      try:
          recomm=username_process(result['username'])
      except:
          print("error")
          pass
          #return(redirect('/'))
      else:
          to_pass=recom_parse(recomm)
          rand_mov=random_movies(10)
          return(render_template('recom_display.html', result=to_pass, random_movies=rand_mov, username=result['username']))
    else:
        return('Not Supported')


@app.route('/ratings', methods = ['POST', 'GET'])
def ratings():
    if request.method == 'POST':
      result = request.form
      processed=process_ratings(result)
      rand_mov=random_movies(10)
      try:
          recomm=username_process(result['username'])
      except:
          pass
          #return(redirect('/'))
      else:
          to_pass=recom_parse(recomm)
          return(render_template('recom_display.html', result=to_pass, random_movies=rand_mov, username=result['username']))
    else:
        return('Not Supported')