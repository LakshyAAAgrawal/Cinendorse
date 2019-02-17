from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
import pickle
#from Recommendation.movie_rec import norm
# from matrix_factorisation import train_model
# from movie_rec import norm
from random import randint
from string import ascii_letters

class recom_vars():
    def __init__(self):
        client=MongoClient()
        # client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
        # client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
        # db=client['deploy_2']
        db=client['try2']
        self.movies=db['movies']
        self.ratings=db['ratings']
        self.users=db['users']
        self.movie_similarity=db['movie_similarity']
        self.np_arrays=db['np_arrays']
        movie_index_dict={}
        user_index_dict={}
        if self.np_arrays.find({'name':'U'}).count()>0:
            user_counter=self.np_arrays.find_one({'name':'U_len'},{'value':1})['value']
            movie_counter=self.np_arrays.find_one({'name':'M_len'},{'value':1})['value']
            for movie in self.movies.find({}, {'_id':1, 'matrix_index':1}):
                try:
                    movie_index_dict[movie['_id']]=movie['matrix_index']
                except:
                    movie_index_dict[movie['_id']]=movie_counter
                    self.movies.update({'_id':movie['_id']}, {'$set':{'matrix_index':movie_counter}})
                    movie_counter+=1
            for user in self.users.find({}, {'_id':1, 'matrix_index':1}):
                try:
                    user_index_dict[user['_id']]=user['matrix_index']
                except:
                    user_index_dict[user['_id']]=user_counter
                    self.users.update({'_id':user['_id']}, {'$set':{'matrix_index':user_counter}})
                    user_counter+=1
        else:
            for movie in self.movies.find({}, {'_id':1}):
                movie_index_dict[movie['_id']]=movie_counter
                self.movies.update({'_id':movie['_id']}, {'$set':{'matrix_index':movie_counter}})
                movie_counter+=1
            user_counter=0
            for user in self.users.find({}, {'_id':1}):
                user_index_dict[user['_id']]=user_counter
                self.users.update({'_id':user['_id']}, {'$set':{'matrix_index':user_counter}})
                user_counter+=1
        ratings_array=np.empty((user_counter, movie_counter))
        ratings_array.fill(np.nan)
        rating_indices=[]
        for rating in self.ratings.find():
            rating_indices.append([user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]])
            ratings_array[user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]]=rating['rating']


        #self.user_mean_array=np.nanmean(ratings_array, axis=1)
        #self.movies_mean_array=np.nanmean(ratings_array, axis=0)
        #self.normalized_user_ratings_array=np.nan_to_num((ratings_array.transpose()-self.user_mean_array).transpose())
        #self.normalized_movies_ratings_array=np.nan_to_num(ratings_array-np.nanmean(ratings_array, axis=0))
        self.movie_similarity_matrix=np.nan_to_num(ratings_array-np.nanmean(ratings_array, axis=0)).transpose().dot(np.nan_to_num(ratings_array-np.nanmean(ratings_array, axis=0)))

        #self.user_similarity_matrix=self.normalized_user_ratings_array.transpose().dot(self.normalized_user_ratings_array)

        self.movie_index_dict=movie_index_dict
        self.user_index_dict=user_index_dict
        self.ratings_array=ratings_array
