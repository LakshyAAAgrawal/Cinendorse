from flask import render_template, redirect
from server import app
from flask import request
import datetime
from Recommendation.movie_rec import username_process
from Recommendation.movie_rec import recommendations
from Recommendation.movie_rec import recom_parse
from Recommendation.movie_rec import random_movies
from Recommendation.movie_rec import process_ratings
from Recommendation.matrix_factorisation import train_model

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        result = request.form
        # print('0', datetime.datetime.now().minute, datetime.datetime.now().second)
        try:
            #This processes the username and returns the user_id of the active user.
            user_id=username_process(result['username'])
        except:
              return(render_template("index.html", error="Special Characters in username not allowed"))
        else:
              recomm=recommendations(user_id, result['algo'])
              to_pass=recom_parse(recomm)
              rand_mov=random_movies(12, result['username'])
              return(render_template('recom_display.html', result=to_pass, random_movies=rand_mov, username=result['username'], algo=result['algo']))
    else:
        return('Not Supported')


@app.route('/ratings', methods = ['POST', 'GET'])
def ratings():
    if request.method == 'POST':
      result = request.form
      processed=process_ratings(result)
      rand_mov=random_movies(15, result['username'])
      try:
          user_id=username_process(result['username'])
          recomm=recommendations(user_id, result['algo'])
      except:
          return(render_template("index.html"))
      else:
          to_pass=recom_parse(recomm)
          return(render_template('recom_display.html', result=to_pass, random_movies=rand_mov, username=result['username'], msg_success="Submitted "+str(processed) +" ratings", algo=result['algo']))
    else:
        return('Not Supported')
