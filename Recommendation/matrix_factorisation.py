import pandas as pd
import numpy as np
from random import randint
from pymongo import MongoClient
from bson.objectid import ObjectId
import pickle
from bson.binary import Binary

# client=MongoClient()
# # client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
# # db=client['deploy_2']
# db=client['try2']
# movies=db['movies']
# ratings=db['ratings']
# users=db['users']
# movie_latent_vector=db['movie_latent_vector']
# user_latent_vector=db['user_latent_vector']
# np_arrays=db['np_arrays']
k=10
def matrix_factorisation(matrix, no_of_users, no_of_movies, rating_indices, U=None, M=None):
    '''
        This function performs the gradient descent for the given data. It is dependent on a modified version of the funk SVD.
    '''
    n=no_of_users
    m=no_of_movies
    epochs=40
    alpha=0.00001
    if U is None: # Rando
        U=np.random.random((n, k))
    if M is None:
        M=np.random.random((m, k))
    for i in range(epochs):
        sq_error=0
        for r_index in rating_indices:
            p=U[r_index[0]]
            q=M[r_index[1]]
            to_change=matrix[r_index[0], r_index[1]]-p.dot(q)
            sq_error=sq_error+pow(to_change, 2)
            U[r_index[0]]=p+alpha*to_change*q
            M[r_index[1]]=q+alpha*to_change*p
        print('Error after', i, 'epochs is', sq_error)
        if sq_error>0.001:
            alpha=0.1
        if sq_error<0.001 and sq_error>0.00001:
            alpha=0.01
        if sq_error<0.00001:
            alpha=0.001
    return(U, M)

def train_model(recom_vars_obj):
    '''
    This function takes the variable holder class as input and then loads the data for both the latent matrices from the database. Verifies for each user, and then, if any new user is found, adds rows and columns for them in the corresponding U and M matrices. The values are picked from a Normal Gaussian centered at 0 with S.D. 1
    After loading of the data, it calls the gradient descent function matrix_factorisation, which returns the updated matrices U and M. It then loads the updated values into the database.
    '''
    movie_counter=0
    if recom_vars_obj.np_arrays.find({'name':'U'}).count()>0:
        U=pickle.loads(recom_vars_obj.np_arrays.find({'name':'U'}).next()['matrix'])
        M=pickle.loads(recom_vars_obj.np_arrays.find({'name':'M'}).next()['matrix'])
        user_counter=len(U)
        movie_counter=len(M)
        for movie in recom_vars_obj.movies.find():
            try:
                recom_vars_obj.movie_index_dict[movie['_id']]=movie['matrix_index']
            except:
                recom_vars_obj.movie_index_dict[movie['_id']]=movie_counter
                recom_vars_obj.movies.update({'_id':movie['_id']}, {'$set':{'matrix_index':movie_counter}})
                M=np.vstack([M, np.random.normal(0,1,[1,k])])
                movie_counter+=1
        for user in recom_vars_obj.users.find():
            try:
                recom_vars_obj.user_index_dict[user['_id']]=user['matrix_index']
            except:
                recom_vars_obj.user_index_dict[user['_id']]=user_counter
                recom_vars_obj.users.update({'_id':user['_id']}, {'$set':{'matrix_index':user_counter}})
                U=np.vstack([U, np.random.normal(0,1,[1,k])])
                user_counter+=1
        recom_vars_obj.ratings_array=np.empty((user_counter, movie_counter))
        recom_vars_obj.ratings_array.fill(np.nan)
        rating_indices=[]
        for rating in recom_vars_obj.ratings.find():
            rating_indices.append([recom_vars_obj.user_index_dict[rating['user_id']], recom_vars_obj.movie_index_dict[rating['movie_id']]])
            recom_vars_obj.ratings_array[recom_vars_obj.user_index_dict[rating['user_id']], recom_vars_obj.movie_index_dict[rating['movie_id']]]=rating['rating']
        new_U, new_M=matrix_factorisation(recom_vars_obj.ratings_array, user_counter, movie_counter, rating_indices, U, M)
    else:
        for movie in recom_vars_obj.movies.find():
            recom_vars_obj.movie_index_dict[movie['_id']]=movie_counter
            recom_vars_obj.movies.update({'_id':movie['_id']}, {'$set':{'matrix_index':movie_counter}})
            movie_counter+=1
        user_counter=0
        for user in recom_vars_obj.users.find():
            recom_vars_obj.user_index_dict[user['_id']]=user_counter
            recom_vars_obj.users.update({'_id':user['_id']}, {'$set':{'matrix_index':user_counter}})
            user_counter+=1
        recom_vars_obj.ratings_array=np.empty((user_counter, movie_counter))
        recom_vars_obj.ratings_array.fill(np.nan)
        rating_indices=[]
        print("4")
        for rating in recom_vars_obj.ratings.find():
            rating_indices.append([recom_vars_obj.user_index_dict[rating['user_id']], recom_vars_obj.movie_index_dict[rating['movie_id']]])
            recom_vars_obj.ratings_array[recom_vars_obj.user_index_dict[rating['user_id']], recom_vars_obj.movie_index_dict[rating['movie_id']]]=rating['rating']
        new_U, new_M=matrix_factorisation(recom_vars_obj.ratings_array, user_counter, movie_counter, rating_indices)
    recom_vars_obj.np_arrays.update({'name':'U'}, {'$set':{'matrix':Binary(pickle.dumps(new_U))}}, upsert=True)
    recom_vars_obj.np_arrays.update({'name':'U_len'}, {'$set':{'value':len(U)}}, upsert=True)
    recom_vars_obj.np_arrays.update({'name':'M'}, {'$set':{'matrix':Binary(pickle.dumps(new_M))}}, upsert=True)
    recom_vars_obj.np_arrays.update({'name':'M_len'}, {'$set':{'value':len(M)}}, upsert=True)

def rating_for(n, user_id, a):
    '''
        This function returns a list of n movies expected to be most highly rated by the users based on predictions from matrix factorisation.
    '''
    if a.np_arrays.find({'name':'U'}).count()>0:
        U=pickle.loads(a.np_arrays.find({'name':'U'})[0]['matrix'])
        M=pickle.loads(a.np_arrays.find({'name':'M'})[0]['matrix'])
    else:
        train_model()
        U=pickle.loads(a.np_arrays.find({'name':'U'})[0]['matrix'])
        M=pickle.loads(a.np_arrays.find({'name':'M'})[0]['matrix'])
    p_user=U[a.users.find({'_id':user_id}).next()['matrix_index']]
    ratings_l=[]
    # print('username', a.users.find_one({'_id':user_id})['username'])
    # print('username', a.users.find({'_id':user_id})[0]['username'])
    # for movie_id in a.ratings.distinct('movie_id', {'user_id':{'$ne':user_id}}):
    not_to_take=a.ratings.distinct('movie_id', {'user_id':user_id})
    for movie_id in a.ratings.find({'movie_id':{'$nin':not_to_take}}).distinct('movie_id'):
        q=M[a.movie_index_dict[movie_id]]
        ratings_l.append([p_user.dot(q), movie_id])
    ratings_l.sort(reverse=True)
    return(ratings_l[:n])
