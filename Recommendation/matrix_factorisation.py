import pandas as pd
import numpy as np
from random import randint
from pymongo import MongoClient
from bson.objectid import ObjectId
import pickle
from bson.binary import Binary

client=MongoClient()
db=client['try']
movies=db['movies']
ratings=db['ratings']
users=db['users']
movie_latent_vector=db['movie_latent_vector']
user_latent_vector=db['user_latent_vector']

def matrix_factorisation(matrix, no_of_users, no_of_movies, rating_indices):
    k=10
    n=no_of_users
    m=no_of_movies
    epochs=10
    alpha=0.01
    U=np.random.random((n, k))
    M=np.random.random((m, k))
    for _ in range(epochs):
        for r_index in rating_indices:
            p=U[r_index[0]]
            q=M[r_index[1]]
            to_change=matrix[r_index[0], r_index[1]]-p.dot(q)
            p=p+alpha*to_change*q
            q=q+alpha*to_change*p
    return(U, M)

def update_exp_ratings_factorisation():
    global users, movies, ratings, exp_ratings_factorisation
    movie_index_dict={}
    user_index_dict={}
    movie_counter=0
    for movie in movies.find():
        movie_index_dict[movie['_id']]=movie_counter
        movie_counter+=1
    user_counter=0
    for user in users.find():
        user_index_dict[user['_id']]=user_counter
        user_counter+=1
    ratings_array=np.empty((user_counter, movie_counter))
    ratings_array.fill(np.nan)
    rating_indices=[]
    for rating in ratings.find():
        rating_indices.append([user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]])
        ratings_array[user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]]=rating['rating']

    U, M=matrix_factorisation(ratings_array, user_counter, movie_counter, rating_indices)
    print('calculated')
    i=0
    for movie in movie_index_dict:
        movie_latent_vector.update({'movie_id':movie}, {'movie_id':movie, 'latent_vector':Binary(pickle.dumps(M[movie_index_dict[movie]]))}, upsert=True)
    for user in user_index_dict:
        user_latent_vector.update({'user_id':user}, {'user_id':user, 'latent_vector':Binary(pickle.dumps(U[user_index_dict[user]]))}, upsert=True)

def recommend_user(n, user_id):
    global users, movies, ratings, exp_ratings_factorisation, movie_latent_vector, user_latent_vector
    ratings_l=[]
    try:
        p=pickle.loads(user_latent_vector.find({'user_id':user_id})[0]['latent_vector'])
    except:
        update_exp_ratings_factorisation()
        p=pickle.loads(user_latent_vector.find({'user_id':user_id})[0]['latent_vector'])
    for movie in movies.find():
        q=pickle.loads(movie_latent_vector.find({'movie_id':movie['_id']})[0]['latent_vector'])
        ratings_l.append([p.dot(q), movie['_id']])
    ratings_l.sort(reverse=True)
    print(ratings_l)
    return(ratings_l[:n])
