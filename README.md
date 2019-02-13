# Cinendorse
This is a project developed as an entry project for Precog.
It gives Movie recommendations to the user based on data collected from them in the form of ratings to movies from a database of 5000 movies.

# Data Collection
For the purpose of collecting data on movies, I wrote the Data_Scraping/main.py script, which takes an integer i as input, and scrapes data for i pages from the IMDB advanced search pages, each having 250 movie, which display all the details about the movies in a single page. I chose to scrape data for the "Most Rated" movies, and not "Highly Rated Movies" so as to ensure that my database does get almost all relatable movies to the target userbase around me.

I chose to work totally on primary data, for which I chose to create the very minimalistic website very early, so as to get primary data on movie ratings from a lot of people I know. The movies displayed for being rated, half of them have been rated by at least one other user, and the other half were randomly picked from a list of movies not rated. This ensured that I got overlapping ratings as well as ratings on more movies in the database.

I was able to collect Data under the heads of "Title", "Year of release", "Synopsis", "License", "Thumbnail Image", "IMDB Rating", "Metascore rating", "Genre", "Run Time", "Directors" and "Cast".

I was able to get 784 Ratings on these movies from about 100 users at the time of this writing.

#Working
When opened, the user is greeted with a form to create a username. I chose not to create a login with a password, as it would have prevented people from signing up and voting, and also because this wouldn't be a security issue. The user creates a username and is then shown a list of Movies to rate. The user is expected to rate only those movies they watched and give ratings according to their own personal understanding.

In another tab, the user can see the movies recommended to them based on the algorithm they choose(through a drop down present). As the user submits more ratings, the recommendations change, and gradually get better.

#Algorithms
## User User Collaborative Filtering
The algorithm maintains the similarity score between a user with each other. For the active user, the algorithm selects "k"(currently 5) most similar users, and all the movies they have rated( Similarity is based on cosine similarity on normalized ratings vector). Then the algorithm determines the expected rating the active user would give to the movies among those to be considered. It sorts the list and returns top n.
It is implemented in the u2_collab function in Recommendation/movie_rec.py

## Item Item Collaborative Filtering
The algorithm identifies all the movies in the database which have at least one rating and which have not been rated by the active user. For each such movie, it finds the similarity of the active movie with all other movies rated by the active user. For each such movie, if the similarity>0, then the rating is included in the weighted mean of the ratings. At the end, this normalized expected rating is added to the mean rating of the current movie. The list of such movies is then sorted based on rating and top n are returned.

## Matrix Factorisation
The algorithm uses a modified version of Funk SVD.
