class movie(object):
    def __init__(self, title, year_of_release, license, run_time, genre_list, imdb_rating, meta_score, synopsis, director_list, cast_list, thumbnail_url):
        self.title=title
        self.year_of_release=year_of_release
        self.license=license
        self.run_time=run_time
        self.genre_list=genre_list
        self.imdb_rating=imdb_rating
        self.meta_score=meta_score
        self.synopsis=synopsis
        self.director_list=director_list
        self.cast_list=cast_list
        self.thumbnail_url=thumbnail_url

    def toDict(self):
        to_ret={'title':self.title, \
                'year_of_release':self.year_of_release, \
                'license':self.license, \
                'runtime':self.run_time, \
                'genres':self.genre_list, \
                'imdb_rating':self.imdb_rating, \
                'metascore':self.meta_score, \
                'synpsis':self.synopsis, \
                'directors':self.director_list, \
                'cast': self.cast_list,\
                'thumbnail_url':self.thumbnail_url \
            }
        return(to_ret)
