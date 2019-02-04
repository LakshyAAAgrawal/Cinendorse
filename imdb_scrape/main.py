import requests
from bs4 import BeautifulSoup
from movie import movie
from time import sleep
from pymongo import MongoClient
client=MongoClient('mongodb://admin:mLabAdmin1000@ds119755.mlab.com:19755/movie_database')
db=client['movie_database']
movie_collection=db['movies']
for i in range(int(input()), int(input())):
    url='https://www.imdb.com/search/title?title_type=feature&sort=num_votes,desc&count=250&start='+str(i*250+1)+'&ref_=adv_nxt'
    response = requests.get(url)
    html_parsed=BeautifulSoup(response.text, 'html.parser')
    movie_containers=html_parsed.findAll('div', class_='lister-item mode-advanced')
    #print(len(movie_containers))
    for movie_container in movie_containers:
        content=movie_container.find('div', class_='lister-item-content')
        title=content.h3.a.text
        year_of_release=content.find('span', class_='lister-item-year text-muted unbold').text[1:-1]
        license=content.p.span.text
        run_time=content.p.find('span', class_='runtime').text
        genre_list=content.p.find('span', class_='genre').text.strip().split(', ')
        imdb_rating=float(content.find('div', class_='ratings-bar').div['data-value'])
        meta_score_container=content.find('div', class_='inline-block ratings-metascore')
        if meta_score_container!=None:
            meta_score=int(meta_score_container.span.text.strip())
        else:
            meta_score=None
        synopsis=content.findAll('p', class_="text-muted")[1].text.strip()

        dir_and_cast_text=content.find('p', class_='').text.strip()
        dir_and_cast_text=" ".join(dir_and_cast_text.replace('\n', '').split())
        dir_end=dir_and_cast_text.find("|")
        star_index=dir_and_cast_text.find("Stars")
        dir_list=dir_and_cast_text[dir_and_cast_text.find(":")+1:dir_end].split(", ")
        cast_list=dir_and_cast_text[star_index+6:].split(", ")

        image_url=movie_container.find('div', class_='lister-item-image float-left').a.img.get("loadlate")[:-22]+"182_CR0,0,182,268_AL__QL50.jpg"
        movie_obj=movie(title, year_of_release, license, run_time, genre_list, imdb_rating, meta_score, synopsis, dir_list, cast_list, image_url)

        movie_collection.insert_one(movie_obj.toDict())
    sleep(0.1)
