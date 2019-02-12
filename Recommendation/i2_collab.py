from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
import pickle

from Recommendation.matrix_factorisation import train_model
#from Recommendation.movie_rec import norm
# from matrix_factorisation import train_model
# from movie_rec import norm
from random import randint
from string import ascii_letters
from Recommendation.recom_vars import recom_vars
print("79")
# client=MongoClient()
client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
print("80")
# db=client['try2']
db=client['deploy_2']
movies=db['movies']
ratings=db['ratings']
users=db['users']
movie_similarity=db['movie_similarity']
np_arrays=db['np_arrays']
print("81")
a=recom_vars()
print("82")

def norm(v):
  sum = float(0)
  for i in range(len(v)):
    sum += v[i]**2
  return sum**(0.5)

def rating_for(user_id, movie_id, algorithm='u2_collab'):
    if algorithm=='i2_collab':
        item_mean=np.nanmean(a.ratings_array, axis=0)[a.movie_index_dict[movie_id]]
        bias=0
        sum_weights=0
        for rating in ratings.find({'user_id':user_id, 'movie_id':{'$ne':movie_id}}):
            weight=a.movie_similarity_matrix[a.movie_index_dict[movie_id], a.movie_index_dict[rating['movie_id']]]
            if weight>0:
                # bias=bias+weight*(a.normalized_movies_ratings_array[a.user_index_dict[user_id], a.movie_index_dict[rating['movie_id']]])
                bias=bias+weight*(np.nan_to_num(a.ratings_array-np.nanmean(a.ratings_array, axis=0))[a.user_index_dict[user_id], a.movie_index_dict[rating['movie_id']]])
                sum_weights=sum_weights+abs(weight)
        if sum_weights!=0:
            exp_rating=item_mean+bias/sum_weights
        else:
            exp_rating=0
        return(exp_rating)

def recommendations_for(n, user_id, algorithm='i2'):
    rating_list=[]
    if algorithm=='i2':
        for rating in ratings.find({'user_id':{'$ne':user_id}}):
            fla=True
            for r in rating_list:
                if r[1]==rating['movie_id']:
                    fla=False
                    continue
            if fla:
                rating_list.append([rating_for(user_id, rating['movie_id'], algorithm='i2_collab'), rating['movie_id']])
        rating_list.sort(reverse=True)
    else:
        None
    return(rating_list[:n])
