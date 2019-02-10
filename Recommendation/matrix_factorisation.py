import pandas as pd
import numpy as np
from random import randint
from pymongo import MongoClient
from bson.objectid import ObjectId
import pickle
from bson.binary import Binary

#client=MongoClient()
client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
db=client['deploy_2']
movies=db['movies']
ratings=db['ratings']
users=db['users']
movie_latent_vector=db['movie_latent_vector']
user_latent_vector=db['user_latent_vector']
np_arrays=db['np_arrays']
k=10
def matrix_factorisation(matrix, no_of_users, no_of_movies, rating_indices, U=None, M=None):
    global k
    n=no_of_users
    m=no_of_movies
    epochs=10
    alpha=0.001
    if U is None:
        U=np.random.random((n, k))
    if M is None:
        M=np.random.random((m, k))
    for _ in range(epochs):
        for r_index in rating_indices:
            p=U[r_index[0]]
            q=M[r_index[1]]
            to_change=matrix[r_index[0], r_index[1]]-p.dot(q)
            p=p+alpha*to_change*q
            q=q+alpha*to_change*p
    return(U, M)

def train_model():
    global users, movies, ratings, exp_ratings_factorisation, k
    movie_index_dict={}
    user_index_dict={}
    movie_counter=0
    if np_arrays.find({'name':'U'}).count()>0:
        U=pickle.loads(np_arrays.find({'name':'U'}).next()['matrix'])
        M=pickle.loads(np_arrays.find({'name':'M'}).next()['matrix'])
        user_counter=len(U)
        movie_counter=len(M)
        for movie in movies.find():
            try:
                movie_index_dict[movie['_id']]=movie['matrix_index']
            except:
                movie_index_dict[movie['_id']]=movie_counter
                movies.update({'_id':movie['_id']}, {'$set':{'matrix_index':movie_counter}})
                M=np.vstack([M, np.random.random([1,k])])
                movie_counter+=1
        for user in users.find():
            try:
                user_index_dict[user['_id']]=user['matrix_index']
            except:
                user_index_dict[user['_id']]=user_counter
                users.update({'_id':user['_id']}, {'$set':{'matrix_index':user_counter}})
                U=np.vstack([U, np.random.random([1,k])])
                user_counter+=1
        ratings_array=np.empty((user_counter, movie_counter))
        ratings_array.fill(np.nan)
        rating_indices=[]
        for rating in ratings.find():
            rating_indices.append([user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]])
            ratings_array[user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]]=rating['rating']
        new_U, new_M=matrix_factorisation(ratings_array, user_counter, movie_counter, rating_indices, U, M)
    else:
        for movie in movies.find():
            movie_index_dict[movie['_id']]=movie_counter
            movies.update({'_id':movie['_id']}, {'$set':{'matrix_index':movie_counter}})
            movie_counter+=1
        user_counter=0
        for user in users.find():
            user_index_dict[user['_id']]=user_counter
            users.update({'_id':user['_id']}, {'$set':{'matrix_index':user_counter}})
            user_counter+=1
        ratings_array=np.empty((user_counter, movie_counter))
        ratings_array.fill(np.nan)
        rating_indices=[]
        print("4")
        for rating in ratings.find():
            rating_indices.append([user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]])
            ratings_array[user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]]=rating['rating']
        new_U, new_M=matrix_factorisation(ratings_array, user_counter, movie_counter, rating_indices)
    np_arrays.update({'name':'U'}, {'$set':{'matrix':Binary(pickle.dumps(new_U))}}, upsert=True)
    np_arrays.update({'name':'M'}, {'$set':{'matrix':Binary(pickle.dumps(new_M))}}, upsert=True)

'''
#def update_exp_ratings_factorisation():
def rating_for(n, user_id):
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
    p_user=U[user_index_dict[user_id]]
    ratings_l=[]
    for movie in movies.find():
        q=M[movie_index_dict[movie['_id']]]
        ratings_l.append([p_user.dot(q), movie['_id']])
    ratings_l.sort(reverse=True)
    return(ratings_l[:n])
    \'''
    for movie in movie_index_dict:
        movie_latent_vector.update({'movie_id':movie}, {'movie_id':movie, 'latent_vector':Binary(pickle.dumps(M[movie_index_dict[movie]]))}, upsert=True)
    for user in user_index_dict:
        user_latent_vector.update({'user_id':user}, {'user_id':user, 'latent_vector':Binary(pickle.dumps(U[user_index_dict[user]]))}, upsert=True)
    \'''
'''

def rating_for(n, user_id):
    global users, movies, ratings, exp_ratings_factorisation
    if np_arrays.find({'name':'U'}).count()>0:
        U=pickle.loads(np_arrays.find({'name':'U'})[0]['matrix'])
        M=pickle.loads(np_arrays.find({'name':'M'})[0]['matrix'])
    else:
        train_model()
        U=pickle.loads(np_arrays.find({'name':'U'})[0]['matrix'])
        M=pickle.loads(np_arrays.find({'name':'M'})[0]['matrix'])
    p_user=U[users.find({'_id':user_id}).next()['matrix_index']]
    ratings_l=[]
    for movie in movies.find():
        q=M[movie['matrix_index']]
        ratings_l.append([p_user.dot(q), movie['_id']])
    ratings_l.sort(reverse=True)
    return(ratings_l[:n])




def recommend_user(n, user_id):
    '''
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
    '''
    return(rating_for(n, user_id))
