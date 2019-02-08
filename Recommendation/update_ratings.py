from random import randint
from random import uniform
from random import choices
from bson.objectid import ObjectId
from pymongo import MongoClient
import string
client=MongoClient('mongodb://admin:mLabAdmin1000@ds119755.mlab.com:19755/movie_database')
db=client['movie_database']
movies=db['movies']
ratings=db['ratings']
users=db['users']
user_ids=[ObjectId('5c58799afaea1331935fda2c'), ObjectId('5c587a02faea1331f3c8f128'), ObjectId('5c587a19faea1331fba7adef')]
for user_id in user_ids:
    #username=''.join(choices(string.ascii_uppercase + string.digits, k=10))
    #user_dict={'username':username}
    #user_id=users.insert_one(user_dict).inserted_id
    #print(dir(user_id))
    movies_to_skip=randint(1,250)
    for i in range(randint(0,5),randint(8,20)):
        movie=movies.find().skip(i*movies_to_skip).next()
        if movie['metascore']==None:
            rating=movie['imdb_rating']+uniform(-1.5,1.5)
            while rating>9.9:
                rating=rating-uniform(0,2)
            while rating<0.1:
                rating=rating+uniform(0,2)
        else:
            w=uniform(0.1,0.9)
            rating=((1-w)*movie['imdb_rating']+w*0.1*movie['metascore'])
        rating=rating/2
        to_enter={'user_id':user_id, 'movie_id': movie['_id'], 'rating':rating}
        ratings.insert_one(to_enter)