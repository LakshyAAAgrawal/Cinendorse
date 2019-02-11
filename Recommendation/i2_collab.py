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

#client=MongoClient()
client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
#client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
db=client['deploy_2']
#db=client['try2']
movies=db['movies']
ratings=db['ratings']
users=db['users']
movie_similarity=db['movie_similarity']
np_arrays=db['np_arrays']
normalized_ratings_array=None

movie_index_dict={}
user_index_dict={}
ratings_array=None
normalized_user_ratings_array=None
normalized_movies_ratings_array=None
user_mean_array=None
movie_similarity_matrix=None
user_similarity_matrix=None

def norm(v):
  sum = float(0)
  for i in range(len(v)):
    sum += v[i]**2
  return sum**(0.5)

def update_similarity_movies(movie_id):
    global ratings_array, movies, users, movie_index_dict, user_index_dict, queries
    m1=ratings_array[:,movie_index_dict[movie_id]]
    norm_1=norm(m1)
    for movie in movies.find():
        if movie['_id']==movie_id:
            None
        else:
            m2=ratings_array[:,movie_index_dict[movie['_id']]]
            dot=m1.dot(m2)
            norm_2=norm(m2)
            if norm_1==0 or norm_2==0:
                similarity=0
            else:
                similarity=dot/(norm_1*norm_2)
            lis=[movie_id, movie['_id']]
            lis.sort()
            qur={'item_1': lis[0], 'item_2': lis[1], 'similarity': float(similarity)}
            if not qur in queries:
                queries.append(qur)
            #movie_similarity.update({'item_1': lis[0], 'item_2': lis[1]}, {'$set': {'similarity': float(similarity)}}, upsert=True)
            #movie_similarity.insert({'item_1': lis[0], 'item_2': lis[1], 'similarity': float(similarity)})
def update_ratings_matrix():
    global users, movies, ratings, movie_index_dict, user_index_dict, ratings_array, normalized_user_ratings_array, normalized_movies_ratings_array, user_mean_array, movie_similarity_matrix, user_similarity_matrix
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
                M=np.vstack([M, np.random.normal(0,1,[1,k])])
                movie_counter+=1
        for user in users.find():
            try:
                user_index_dict[user['_id']]=user['matrix_index']
            except:
                user_index_dict[user['_id']]=user_counter
                users.update({'_id':user['_id']}, {'$set':{'matrix_index':user_counter}})
                U=np.vstack([U, np.random.normal(0,1,[1,k])])
                user_counter+=1
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
    for rating in ratings.find():
        rating_indices.append([user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]])
        ratings_array[user_index_dict[rating['user_id']], movie_index_dict[rating['movie_id']]]=rating['rating']


    user_mean_array=np.nanmean(ratings_array, axis=1)
    movies_mean_array=np.nanmean(ratings_array, axis=0)
    normalized_user_ratings_array=np.nan_to_num((ratings_array.transpose()-user_mean_array).transpose())
    normalized_movies_ratings_array=np.nan_to_num(ratings_array-movies_mean_array)
    movie_similarity_matrix=normalized_movies_ratings_array.transpose().dot(normalized_movies_ratings_array)
    user_similarity_matrix=normalized_user_ratings_array.transpose().dot(normalized_user_ratings_array)

#Use the dot product of 2 vectors for similarity matrix.. store this continuously. Use this only for both the user user and item item collaborative...

def rating_for(user_id, movie_id, algorithm='u2_collab'):
    global users, movies, ratings, movie_index_dict, user_index_dict, ratings_array, normalized_movies_ratings_array, user_mean_array, normalized_user_ratings_array, movie_similarity_matrix, user_similarity_matrix
    if algorithm=='i2_collab':
        item_mean=np.nanmean(ratings_array, axis=0)[movie_index_dict[movie_id]]
        bias=0
        sum_weights=0
        for rating in ratings.find({'user_id':user_id, 'movie_id':{'$ne':movie_id}}):
            weight=movie_similarity_matrix[movie_index_dict[movie_id], movie_index_dict[rating['movie_id']]]
            if weight>0:
                bias=bias+weight*(normalized_movies_ratings_array[user_index_dict[user_id], movie_index_dict[rating['movie_id']]])
                sum_weights=sum_weights+abs(weight)
        if sum_weights!=0:
            exp_rating=item_mean+bias/sum_weights
        else:
            exp_rating=0
        return(exp_rating)

    if algorithm=='u2_collab':
        user_mean=np.nanmean(ratings_array, axis=1)[user_index_dict[user_id]]
        bias=0
        sum_weights=0
        for rating in ratings.find({'movie_id':movie_id, 'user_id':{'$ne':user_id}}):
            weight=user_similarity_matrix[user_index_dict[user_id], user_index_dict[rating['user_id']]]
            if weight>0:
                bias=bias+weight*(normalized_user_ratings_array[user_index_dict[rating['user_id']], movie_index_dict[movie_id]])
                sum_weights=sum_weights+abs(weight)
        if sum_weights!=0:
            exp_rating=user_mean+bias/sum_weights
        else:
            exp_rating=0
        return(exp_rating)

def recommendations_for(n, user_id, algorithm='i2'):
    global users, movies, ratings, movie_index_dict, user_index_dict, ratings_array, normalized_movies_ratings_array, user_mean_array, normalized_user_ratings_array, movie_similarity_matrix, user_similarity_matrix
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
        '''
        similarity_for_user=user_similarity_matrix[user_index_dict[user_id]]
        users_to_consider=[]
        for user in users.find():
            if user['_id']==user_id:
                None
            if similarity_for_user[user_index_dict[user['_id']]]>0:
                users_to_consider.append(user['_id'])
                for ratin
                for ratings.find
        '''
    return(rating_list[:n])
update_ratings_matrix()
