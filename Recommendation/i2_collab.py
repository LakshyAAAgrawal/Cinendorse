from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
import pickle

from random import randint
from string import ascii_letters
print("80")
print("81")
print("82")

def norm(v):
  sum = float(0)
  for i in range(len(v)):
    sum += v[i]**2
  return sum**(0.5)

def rating_for(user_id, movie_id, arr_1, algorithm='u2_collab', a=None):
    if algorithm=='i2_collab':
        item_mean=np.nanmean(a.ratings_array, axis=0)[a.movie_index_dict[movie_id]]
        bias=0
        sum_weights=0
        for rating in a.ratings.find({'user_id':user_id, 'movie_id':{'$ne':movie_id}}, {'movie_id':1}):
            weight=a.movie_similarity_matrix[a.movie_index_dict[movie_id], a.movie_index_dict[rating['movie_id']]]
            if weight>0:
                bias=bias+weight*(arr_1[a.user_index_dict[user_id], a.movie_index_dict[rating['movie_id']]])
                sum_weights=sum_weights+abs(weight)
        if sum_weights!=0:
            exp_rating=item_mean+bias/sum_weights
        else:
            exp_rating=0
        return(exp_rating)

def recommendations_for(n, user_id, algorithm='i2', a=None):
    rating_list=[]
    arr_1=np.nan_to_num(a.ratings_array-np.nanmean(a.ratings_array, axis=0))
    for m_id in a.ratings.distinct('movie_id', {'user_id':{'$ne':user_id}}):
        rating_list.append([rating_for(user_id, m_id, arr_1, algorithm='i2_collab',a=a), m_id])
    rating_list.sort(reverse=True)
    return(rating_list[:n])
