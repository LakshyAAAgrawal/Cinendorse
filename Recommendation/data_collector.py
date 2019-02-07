#users.create_index('username', unique=True)
from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
from random import randint
#client=MongoClient('mongodb://admin:mLabAdmin1000@ds119755.mlab.com:19755/try')
client=MongoClient('mongodb://admin:mLabAdmin1000@ds221405.mlab.com:21405/try')
db=client['try']
movies=db['movies']
ratings=db['ratings']
users=db['users']

def norm(v):
  sum = float(0)
  for i in range(len(v)):
    sum += v[i]**2
  return sum**(0.5)

def add_user(username, users):
    user_dict={'username':username}
    try:
        user_id=users.insert_one(user_dict).inserted_id
    except:
        pass
    return(user_id)

def add_rating(movie_id, user_id, rating):
    global users, movies, ratings
    to_enter={'user_id':user_id, 'movie_id': movie_id, 'rating':rating}
    ratings.insert_one(to_enter)

    ratings.find_one_and_update({'user_id':user_id, 'movie_id': movie_id}, {'$set': {'rating': float(rating)}}, upsert=True)

    update_ratings_average(user_id)
    #update_similarity_users(user_id)

def update_ratings_average(user_id):
    global users, movies, ratings
    rating_cursor=ratings.find({'user_id':user_id})
    sum=0
    for rating in rating_cursor:
        sum=sum+rating['rating']
    mean=sum/rating_cursor.count()
    users.find_one_and_update({'_id': user_id}, {'$set': {'mean_rating': mean}})

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
            norm_1=norm(user_1)
            norm_2=norm(user_2)
            if norm_1==0 or norm_2==0:
                cosine=0
            else:
                cosine=dot_product/((norm_1)*(norm_2))
            users.find_one_and_update({'_id': user['_id']}, {'$set': {'similarity.'+users.find_one({'_id':user_id})['username']: cosine}})
            users.find_one_and_update({'_id': user_id}, {'$set': {'similarity.'+user['username']: float(cosine)}})
    return(ndf, df)

def recommendations(n, user_id):
    global users, movies, ratings
    user_a=users.find_one({'_id':user_id})
    similarity_dict=user_a['similarity']
    users_to_consider=[]
    movies_to_consider=[]
    for user_2 in similarity_dict:
        if similarity_dict[user_2]>0:
            users_to_consider.append(user_2)
            for rating in ratings.find({'user_id':users.find_one({'username':user_2})['_id']}):
                if not (rating['movie_id'] in movies_to_consider):
                    movies_to_consider.append([None, rating['movie_id']])
    for movie_ls in movies_to_consider:
        i=0


        movie_id=movie_ls[1]


        all_ratings=ratings.find({'movie_id':movie_id})


        mean=user_a['mean_rating']
        bias=0
        sum_weights=0
        for user in users_to_consider:


            similarity=similarity_dict[user]


            sum_weights=sum_weights+similarity


            user_obj=users.find_one({'username':user})


            try:


                bias=bias+similarity*(ratings.find_one({'user_id':user_obj['_id'], 'movie_id':movie_id})['rating']-user_obj['mean_rating'])
            except:
                None
        expectFalseed_rating=bias/sum_weights + mean
        movie_ls[0]=bias/sum_weights + mean
        print(movie_ls)
    movies_to_consider.sort(reverse=True)
    return(movies_to_consider[:15])

if __name__=='__main__':
    error=True
    while error:
        try:
            username=input('Enter username : ')
            if username=='':
                raise Exception()
            if users.find({'username':username}).count()>0:
                user_id=users.find({'username':username})[0]['_id']
                error=False
            else:
                user_id=add_user(username, users)
                error=False
        except:
            error=True
    while True:
        movie_obj=movies.find().skip(randint(0,4999)).next()
        print(movie_obj['title'])
        try:
            in_s=input('Please enter rating, or blank for skip, c for exit : ')
            rating=float(in_s)
            if rating>0 and rating<5.1:
                rating=in_s
            else:
                raise Exception('x should not exceed 5 or less than 0')
        except:
            if in_s=='c':
                break
        else:
            add_rating(movie_obj['_id'], user_id, rating)
