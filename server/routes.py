from flask import render_template, redirect
from server import app
from flask import request
import datetime
import time
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
        print("72")
        time.sleep(3)
        result = request.form
        print('0', datetime.datetime.now().minute, datetime.datetime.now().second)
        try:
            user_id=username_process(result['username'])
        except:
              return(render_template("index.html", error="Special Characters in username not allowed"))
        else:
              recomm=recommendations(user_id)
              to_pass=recom_parse(recomm)
              rand_mov=random_movies(10, result['username'])
              return(render_template('recom_display.html', result=to_pass, random_movies=rand_mov, username=result['username']))
    else:
        return('Not Supported')


@app.route('/ratings', methods = ['POST', 'GET'])
def ratings():
    if request.method == 'POST':
      result = request.form
      processed=process_ratings(result)
      train_model()
      rand_mov=random_movies(15, result['username'])
      try:
          user_id=username_process(result['username'])
          recomm=recommendations(user_id)
      except:
          return(render_template("index.html"))
      else:
          to_pass=recom_parse(recomm)
          return(render_template('recom_display.html', result=to_pass, random_movies=rand_mov, username=result['username'], msg_success="Submitted "+str(processed) +" ratings"))
    else:
        return('Not Supported')
