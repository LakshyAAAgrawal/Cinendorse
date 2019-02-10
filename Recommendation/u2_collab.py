from pymongo import MongoClient
from bson.objectid import ObjectId
import pandas as pd
import numpy as np
from random import randint
from string import ascii_letters
#client=MongoClient('mongodb://admin:mLabAdmin1000@ds119755.mlab.com:19755/try')
#client=MongoClient('mongodb://admin:mLabAdmin1000@ds221405.mlab.com:21405/try')
#client=MongoClient()
client=MongoClient('mongodb://admin:mLabAdmin1000@ds129045.mlab.com:29045/deploy_2')
db=client['deploy_2']
movies=db['movies']
ratings=db['ratings']
users=db['users']
