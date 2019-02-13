#users.create_index('username', unique=True)
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
from random import randint
from string import ascii_letters
import datetime

import Recommendation.matrix_factorisation
from Recommendation.i2_collab import recommendations_for
from Recommendation.recom_vars import recom_vars
a=recom_vars()
# from matrix_factorisation import train_model
# import matrix_factorisation

#client=MongoClient('mongodb://admin:mLabAdmin1000@ds119755.mlab.com:19755/try')
# client=MongoClient('mongodb://admin:mLabAdmin1000@ds221405.mlab.com:21405/try')

def norm(v):
  sum = float(0)
  for i in range(len(v)):
    sum += v[i]**2
  return sum**(0.5)

def add_user(username):
    if username=='' or ('.' in username):
        raise Exception()
    if  not all(c in ascii_letters+'0123456789' for c in username):
        raise Exception()
    user_dict={'username':username, 'similarity':{}}
    try:
        user_id=a.users.insert_one(user_dict).inserted_id
    except:
        pass
    #print(username, 'added as', user_id)
    update_ratings_average(user_id)
    update_similarity_users(user_id)
    Recommendation.matrix_factorisation.train_model(a)
    return(user_id)

def add_rating(movie_id, user_id, rating):
    to_enter={'user_id':user_id, 'movie_id': movie_id, 'rating':rating}
    #print(to_enter)
    a.ratings.insert_one(to_enter)
    #print(rating,'inserted for', movies.find_one({'_id':movie_id})['title'], 'by', users.find_one({'_id':user_id})['username'])
    update_ratings_average(user_id)
    update_similarity_users(user_id)

def update_ratings_average(user_id):
    rating_cursor=a.ratings.find({'user_id':user_id})
    sum=0
    for rating in a.ratings.find({'user_id':user_id}):
        sum=sum+rating['rating']
    no_of_ratings=a.ratings.find({'user_id':user_id}).count()
    if no_of_ratings>0:
        mean=sum/no_of_ratings
    else:
        mean=3
    a.users.find_one_and_update({'_id': user_id}, {'$set': {'mean_rating': mean}}, upsert=True)

def update_ratings_movies(movie_id):
    sum=0
    for rating in a.ratings.find({'movie_id':movie_id}):
        sum=sum+rating['rating']
    mean=sum/a.ratings.find({'movie_id':movie_id}).count()
    a.movies.find_one_and_update({'_id': movie_id}, {'$set': {'mean_rating': mean}})

def update_similarity_users(user_id):
    data_dict={}
    # for  in movies.find():
    #     data_dict[movie['_id']]={}
    # for rating in ratings.find():
    #     data_dict[rating['movie_id']][rating['user_id']]=rating['rating']
    # #print(data_dict)
    # df=pd.DataFrame(data_dict)
    # print(df.mean(axis=1))
    # df.to_csv('before.csv')
    # ndf=df.sub(df.mean(axis=1), axis=0)
    for user in a.users.find():
        data_dict[user['_id']]={}
    for rating in a.ratings.find():
        data_dict[rating['user_id']][rating['movie_id']]=rating['rating']
    df=pd.DataFrame(data_dict)
    ndf=df.sub(df.mean(axis=0), axis=1)
    #might want to divide by standard deviation here!!

    ndf=ndf.fillna(0)
    user_1=ndf[user_id].values
    for user in a.users.find():
        if user['_id']==user_id:
            None
        else:
            user_2=ndf[user['_id']].values
            dot_product=user_1.dot(user_2)
            #print('dot_product', dot_product)
            norm_1=norm(user_1)
            norm_2=norm(user_2)
            if norm_1==0 or norm_2==0:
                cosine=0
            else:
                cosine=dot_product/((norm_1)*(norm_2))
            #print('after cosine', cosine)
            a.users.find_one_and_update({'_id': user['_id']}, {'$set': {'similarity.'+a.users.find_one({'_id':user_id})['username']: cosine}})
            #print(user['username'])
            a.users.find_one_and_update({'_id': user_id}, {'$set': {'similarity.'+user['username']: float(cosine)}}, upsert=True)
    return(ndf, df)

def u2_collab(n, user_id):
    user_a=a.users.find_one({'_id':user_id})
    print('21')
    try:
        similarity_dict=user_a['similarity']
    except:
        update_similarity_users(user_id)
        user_a=a.users.find_one({'_id':user_id})
        similarity_dict=user_a['similarity']
    print('22')
    users_to_consider=[]
    movies_to_consider=[]
    print('23')
    for user_2 in similarity_dict:
        if similarity_dict[user_2]>0:
            users_to_consider.append([similarity_dict[user_2], user_2])
    users_to_consider.sort(reverse=True)
    for user_2_ls in users_to_consider[:5]:
        for rating in a.ratings.find({'user_id':a.users.find_one({'username':user_2_ls[1]}, {'_id':1})['_id']}, {'movie_id':1}):
            if not ([None, rating['movie_id']] in movies_to_consider):
                movies_to_consider.append([None, rating['movie_id']])
    to_ret=[]
    print('24')
    for movie_ls in movies_to_consider:
        i=0
        movie_id=movie_ls[1]
        mean=user_a['mean_rating']
        bias=0
        sum_weights=0
        for user_ls in users_to_consider:
            similarity=similarity_dict[user_ls[1]]
            sum_weights=sum_weights+similarity
            user_obj=a.users.find_one({'username':user_ls[1]}, {'user_id':1, 'mean_rating':1})
            try:
                bias=bias+similarity*(a.ratings.find_one({'user_id':user_obj['_id'], 'movie_id':movie_id}, {'rating':1, '_id':False})['rating']-user_obj['mean_rating'])
            except:
                None
        #movie_ls[0]=bias/sum_weights + mean
        to_ret.append([bias/sum_weights + mean, movie_ls[1]])
        movie_ls=None
    to_ret.sort(reverse=True)
    print('25')
    return(to_ret[:n])

def recom_parse(lis):
    to_ret=[]
    for i in lis:
        dict=a.movies.find_one({'_id':i[1]})
        to_add={'title':dict['title'], \
                'year_of_release':dict['year_of_release'], \
                'license':dict['license'], \
                'runtime':dict['runtime'], \
                'genres':dict['genres'], \
                'synpsis':dict['synpsis'], \
                'directors':dict['directors'], \
                'cast': dict['cast'],\
                'thumbnail_url':dict['thumbnail_url'], \
                'imdb_rating':dict['imdb_rating']
            }
        to_ret.append(to_add)
    return(to_ret)

def rand_movies_for_rating(n, user_id):
    global a
    l=[]
    z=a.ratings.find({'user_id':{'$ne':user_id}})
    for i in range(n//2):
        l.append(z[randint(0,z.count()-1)]['movie_id'])
    return(l)

def random_movies(n, username):
    global a
    to_ret=[]
    user=a.users.find_one({'username':username})
    lis=rand_movies_for_rating(n, user['_id'])
    for l in lis:
        movie_obj=a.movies.find_one({'_id':l})
        to_add={'id':movie_obj['_id'],
                'title':movie_obj['title'], \
                'genres':movie_obj['genres'], \
                'synpsis':movie_obj['synpsis'], \
                'directors':movie_obj['directors'], \
                'cast': movie_obj['cast'],\
                'thumbnail_url':movie_obj['thumbnail_url'], \
                'year_of_release':movie_obj['year_of_release'], \
                'imdb_rating':movie_obj['imdb_rating']
            }
        if to_add in to_ret:
            None
        else:
            to_ret.append(to_add)
    for i in range(n//2):
        movie_obj=a.movies.find({}).skip(randint(0,4999)).next()
        if a.ratings.find({'movie_id':movie_obj['_id'], 'user_id':user['_id']}).count()>0:
            None
        else:
            to_add={'id':movie_obj['_id'],
                    'title':movie_obj['title'], \
                    'genres':movie_obj['genres'], \
                    'synpsis':movie_obj['synpsis'], \
                    'directors':movie_obj['directors'], \
                    'cast': movie_obj['cast'],\
                    'thumbnail_url':movie_obj['thumbnail_url'], \
                    'year_of_release':movie_obj['year_of_release']
                }
            if to_add in to_ret:
                None
            else:
                to_ret.append(to_add)
    return(to_ret)

def process_ratings(form_input):
    #print(form_input['username'])
    user_id=a.users.find_one({'username':form_input['username']})['_id']
    #print(user_id)
    no_of_ratings=0
    for rating in form_input:
        if(rating=='username' or rating=='algo'):
            None
        else:
            if(form_input[rating]=='Null'):
                None
            else:
                add_rating(ObjectId(rating), user_id, float(form_input[rating]))
                no_of_ratings=no_of_ratings+1
    Recommendation.matrix_factorisation.train_model(a)
    return(no_of_ratings)

def recommendations(user_id, algo):
    if algo=='u2':
        l2=u2_collab(30, user_id)
    elif algo=='mf':
        l2=Recommendation.matrix_factorisation.rating_for(30, user_id, a)
    elif algo=='i2':
        l2=recommendations_for(30, user_id, 'i2', a)
    # l2.extend(l1[:10])
    # l2.extend(l3[:10])
    # l2.sort(reverse=True)
    return(l2)

def username_process(username):
    if a.users.find({'username':username}).count()>0:
        user_id=a.users.find_one({'username':username}, {'_id':1})['_id']
    else:
        user_id=add_user(username)
    #return(Recommendation.matrix_factorisation.recommend_user(10, user_id))
    return(user_id)
