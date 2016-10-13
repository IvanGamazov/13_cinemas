import requests
import os
from urllib.request import urlretrieve
from bs4 import BeautifulSoup


def fetch_afisha_page():
    page = 'page.html'
    urlretrieve('http://www.afisha.ru/msk/schedule_cinema/', page)
    return page


def get_movies_from_afisha(divs):
    movie_titles = []
    for div in divs:
        if 'class' in div.attrs and 'object' in div.get('class'):
            cinemas_count = len(div.table.tbody.find_all('tr'))
            block_divs = div.find_all('div')
            name = get_cinema_caption(block_divs)
            movie_titles.append({'name': name, 'cinemas_count': cinemas_count})
    return movie_titles

def get_cinema_caption(div_tags):
    for cinema_div in div_tags:
        if 'class' in cinema_div.attrs and \
                        'm-disp-table' in cinema_div.get('class'):
            return cinema_div.h3.string


def parse_afisha_list(raw_html):
    if os.path.exists(raw_html):
        with open(raw_html) as html_doc:
            soup = BeautifulSoup(html_doc, 'html.parser')
            div_tags = soup.find_all('div')
        return div_tags



def fetch_movie_info(movie_title):
    response = requests.get('http://api.kinopoisk.cf/searchFilms?keyword='+movie_title).json()
    rating = response['searchFilms'][0].get('rating', None)
    try:
        rating = float(rating[0:3])
    except:
        if rating is not None:
            rating = float(rating[:2])/10
        else:
            rating = 0
    return rating

def sort_movies_by_rating(movies):
    movies.sort(key=lambda movie: movie['rating'], reverse=True)
    return movies


def output_movies_to_console(movies):
    for film in movies:
        print(film['caption'], film['rating'], film['cinema_amount'])


def get_full_info(movies):
    films = []
    for movie in movies:
        films.append({'caption': movie['name'], 'rating': fetch_movie_info(movie['name']), 'cinema_amount': movie['cinemas_count']})
    return films


def in_lots_of_cinemas(min_cinemas_amount, movies):
    films = []
    for movie in movies:
        if int(movie['cinema_amount'])>min_cinemas_amount:
            films.append(movie)
    return films


if __name__ == '__main__':
    html_page = fetch_afisha_page()
    html_page = 'page.html'
    page_div_tags = parse_afisha_list(html_page)
    afisha_movies = get_movies_from_afisha(page_div_tags)
    movies = get_full_info(afisha_movies)
    films = sort_movies_by_rating(movies)
    movies = in_lots_of_cinemas(10, films)
    output_movies_to_console(movies)
