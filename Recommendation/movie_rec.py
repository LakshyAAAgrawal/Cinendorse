#users.create_index('username', unique=True)
import time
print("60")
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

# client=MongoClient()
client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
db=client['deploy_2']
# db=client['try2']
movies=db['movies']
ratings=db['ratings']
users=db['users']
def norm(v):
  sum = float(0)
  for i in range(len(v)):
    sum += v[i]**2
  return sum**(0.5)

def add_user(username):
    global users
    if username=='' or ('.' in username):
        raise Exception()
    if  not all(c in ascii_letters+'0123456789' for c in username):
        raise Exception()
    user_dict={'username':username, 'similarity':{}}
    try:
        user_id=users.insert_one(user_dict).inserted_id
    except:
        pass
    #print(username, 'added as', user_id)
    update_ratings_average(user_id)
    update_similarity_users(user_id)
    Recommendation.matrix_factorisation.train_model(a)
    return(user_id)

def add_rating(movie_id, user_id, rating):
    global users, movies, ratings
    to_enter={'user_id':user_id, 'movie_id': movie_id, 'rating':rating}
    #print(to_enter)
    ratings.insert_one(to_enter)
    #print(rating,'inserted for', movies.find_one({'_id':movie_id})['title'], 'by', users.find_one({'_id':user_id})['username'])
    update_ratings_average(user_id)
    update_similarity_users(user_id)

def update_ratings_average(user_id):
    global users, movies, ratings
    rating_cursor=ratings.find({'user_id':user_id})
    sum=0
    for rating in ratings.find({'user_id':user_id}):
        sum=sum+rating['rating']
    no_of_ratings=ratings.find({'user_id':user_id}).count()
    if no_of_ratings>0:
        mean=sum/no_of_ratings
    else:
        mean=3
    users.find_one_and_update({'_id': user_id}, {'$set': {'mean_rating': mean}}, upsert=True)

def update_ratings_movies(movie_id):
    global users, movies, ratings
    rating_cursor=ratings.find({'movie_id':movie_id})

    sum=0
    for rating in ratings.find({'movie_id':movie_id}):
        sum=sum+rating['rating']
    mean=sum/ratings.find({'movie_id':movie_id}).count()
    movies.find_one_and_update({'_id': movie_id}, {'$set': {'mean_rating': mean}})

def update_similarity_users(user_id):
    global users, movies, ratings
    user_cursor=users.find()
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
    for user in users.find():
        data_dict[user['_id']]={}
    for rating in ratings.find():
        data_dict[rating['user_id']][rating['movie_id']]=rating['rating']
    df=pd.DataFrame(data_dict)
    ndf=df.sub(df.mean(axis=0), axis=1)
    #might want to divide by standard deviation here!!

    ndf=ndf.fillna(0)
    user_1=ndf[user_id].values
    for user in users.find():
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
            users.find_one_and_update({'_id': user['_id']}, {'$set': {'similarity.'+users.find_one({'_id':user_id})['username']: cosine}})
            #print(user['username'])
            users.find_one_and_update({'_id': user_id}, {'$set': {'similarity.'+user['username']: float(cosine)}}, upsert=True)
    return(ndf, df)

def u2_collab(n, user_id):
    global users, movies, ratings
    user_a=users.find_one({'_id':user_id})
    print('21', datetime.datetime.now().minute, datetime.datetime.now().second)
    try:
        similarity_dict=user_a['similarity']
    except:
        update_similarity_users(user_id)
        user_a=users.find_one({'_id':user_id})
        similarity_dict=user_a['similarity']
    print('22', datetime.datetime.now().minute, datetime.datetime.now().second)
    users_to_consider=[]
    movies_to_consider=[]
    print('23', datetime.datetime.now().minute, datetime.datetime.now().second)
    for user_2 in similarity_dict:
        if similarity_dict[user_2]>0:
            users_to_consider.append(user_2)
            for rating in ratings.find({'user_id':users.find_one({'username':user_2})['_id']}):
                if not ([None, rating['movie_id']] in movies_to_consider):
                    movies_to_consider.append([None, rating['movie_id']])
    to_ret=[]
    print('24', datetime.datetime.now().minute, datetime.datetime.now().second)
    for movie_ls in movies_to_consider:
        i=0
        movie_id=movie_ls[1]
        mean=user_a['mean_rating']
        bias=0
        sum_weights=0
        for user in users_to_consider:
            similarity=similarity_dict[user]
            sum_weights=sum_weights+similarity
            user_obj=users.find_one({'username':user}, {'user_id':1, 'mean_rating':1})
            try:
                bias=bias+similarity*(ratings.find_one({'user_id':user_obj['_id'], 'movie_id':movie_id}, {'rating':1, '_id':False})['rating']-user_obj['mean_rating'])
            except:
                None
        #movie_ls[0]=bias/sum_weights + mean
        to_ret.append([bias/sum_weights + mean, movie_ls[1]])
    to_ret.sort(reverse=True)
    print('25', datetime.datetime.now().minute, datetime.datetime.now().second)
    return(to_ret[:n])

def recom_parse(lis):
    global users, movies, ratings
    to_ret=[]
    for i in lis:
        dict=movies.find_one({'_id':i[1]})
        to_add={'title':dict['title'], \
                'year_of_release':dict['year_of_release'], \
                'license':dict['license'], \
                'runtime':dict['runtime'], \
                'genres':dict['genres'], \
                'synpsis':dict['synpsis'], \
                'directors':dict['directors'], \
                'cast': dict['cast'],\
                'thumbnail_url':dict['thumbnail_url'] \
            }
        to_ret.append(to_add)
    return(to_ret)

def rand_movies_for_rating(n, user_id):
    l=[]

    a=ratings.find({'user_id':{'$ne':user_id}})
    for i in range(n//2):
        l.append(a[randint(0,a.count()-1)]['movie_id'])
    return(l)

def random_movies(n, username):
    to_ret=[]
    user=users.find_one({'username':username})
    lis=rand_movies_for_rating(n, user['_id'])
    for l in lis:
        movie_obj=movies.find_one({'_id':l})
        to_add={'id':movie_obj['_id'],
                'title':movie_obj['title'], \
                'genres':movie_obj['genres'], \
                'synpsis':movie_obj['synpsis'], \
                'directors':movie_obj['directors'], \
                'cast': movie_obj['cast'],\
                'thumbnail_url':movie_obj['thumbnail_url'] \
            }
        if to_add in to_ret:
            None
        else:
            to_ret.append(to_add)
    for i in range(n//2):
        movie_obj=movies.find({}).skip(randint(0,4999)).next()
        if ratings.find({'movie_id':movie_obj['_id'], 'user_id':user['_id']}).count()>0:
            None
        else:
            to_add={'id':movie_obj['_id'],
                    'title':movie_obj['title'], \
                    'genres':movie_obj['genres'], \
                    'synpsis':movie_obj['synpsis'], \
                    'directors':movie_obj['directors'], \
                    'cast': movie_obj['cast'],\
                    'thumbnail_url':movie_obj['thumbnail_url'] \
                }
            if to_add in to_ret:
                None
            else:
                to_ret.append(to_add)
    return(to_ret)

def process_ratings(form_input):
    #print(form_input['username'])
    user_id=users.find_one({'username':form_input['username']})['_id']
    #print(user_id)
    no_of_ratings=0
    for rating in form_input:
        if(rating=='username'):
            None
        else:
            if(form_input[rating]=='Null'):
                None
            else:
                add_rating(ObjectId(rating), user_id, float(form_input[rating]))
                no_of_ratings=no_of_ratings+1
    Recommendation.matrix_factorisation.train_model(a)
    return(no_of_ratings)

def recommendations(user_id):

    print('10', datetime.datetime.now().minute, datetime.datetime.now().second)
    l1=u2_collab(10, user_id)
    print('11', datetime.datetime.now().minute, datetime.datetime.now().second)
    l2=Recommendation.matrix_factorisation.recommend_user(10, user_id)
    print('12', datetime.datetime.now().minute, datetime.datetime.now().second)
    l3=recommendations_for(10, user_id, 'i2', a)
    print('13', datetime.datetime.now().minute, datetime.datetime.now().second)
    l2.extend(l1[:10])
    l2.extend(l3[:10])
    print('14', datetime.datetime.now().minute, datetime.datetime.now().second)
    l2.sort(reverse=True)
    print('15', datetime.datetime.now().minute, datetime.datetime.now().second)
    return(l2)

    # return([[10, movies.find_one({}, {'_id':1})['_id']]])

def username_process(username):
    if users.find({'username':username}).count()>0:
        user_id=users.find_one({'username':username}, {'_id':1})['_id']
    else:
        user_id=add_user(username)
    #return(Recommendation.matrix_factorisation.recommend_user(10, user_id))
    return(user_id)
