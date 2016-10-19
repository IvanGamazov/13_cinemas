import requests
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from tempfile import NamedTemporaryFile

PAGE_URL = 'http://www.afisha.ru/msk/schedule_cinema/'
KINOPOISK_SEARCH_API = 'http://api.kinopoisk.cf/searchFilms'


def fetch_afisha_page():
    page = NamedTemporaryFile()
    urlretrieve(PAGE_URL, page.name)
    return page


def get_film_info_from_div(div):
    cinemas_count = len(div.table.tbody.find_all('tr'))
    block_divs = div.find_all('div')
    name = get_cinema_caption(block_divs)
    return {'name': name, 'cinemas_count': cinemas_count}


def get_movies_from_afisha(divs):
    movie_divs = list(filter(lambda div: 'class' in div.attrs and
                                         'object' in div.get('class'), divs))
    movies = list(map(lambda div: get_film_info_from_div(div), movie_divs))
    return movies


def get_cinema_caption(div_tags):
    for cinema_div in div_tags:
        if 'class' in cinema_div.attrs and \
                        'm-disp-table' in cinema_div.get('class'):
            return cinema_div.h3.string


def parse_afisha_list(raw_html_file):
    soup = BeautifulSoup(raw_html_file.read(), 'html.parser')
    div_tags = soup.find_all('div')
    return div_tags


def fetch_movie_info(movie_title):
    payload = {'keyword': movie_title}
    response = requests.get(KINOPOISK_SEARCH_API, params=payload).json()
    rating = response['searchFilms'][0].get('rating', None)
    try:
        rating = float(rating[0:3])
    except ValueError:
        if rating is not None:
            rating = float(rating[:2]) / 10
        else:
            rating = 0
    return rating


def sort_movies_by_rating(movies):
    sorted_movies = movies
    sorted_movies.sort(key=lambda movie: movie['rating'], reverse=True)
    return sorted_movies


def output_movies_to_console(movies, films_number):
    for film in movies[:films_number]:
        print('Название -', film['caption'],
              '- рейтинг -', film['rating'],
              ' доступно кинотеатров -',
              film['cinema_amount'])


def get_full_info(movies):
    films = []
    for movie in movies:
        films.append({'caption': movie['name'], 'rating': fetch_movie_info(movie['name']),
                      'cinema_amount': movie['cinemas_count']})
    return films


def films_in_lots_of_cinemas(min_cinemas_amount, movies):
    films = list(filter(lambda film: int(film['cinema_amount']) > min_cinemas_amount, movies))
    return films

if __name__ == '__main__':
    min_cinemas = int(input('В скольких кинотеатрах '
                            '(минимум) должен идти фильм? --> '))
    films_needed = int(input('Сколько фильмов вывести? --> '))
    html_page_name = fetch_afisha_page()
    page_div_tags = parse_afisha_list(html_page_name)
    afisha_movies = get_movies_from_afisha(page_div_tags)
    movies = get_full_info(afisha_movies)
    films_in_many_cinemas = sort_movies_by_rating(movies)
    movies_in_cinemas = films_in_lots_of_cinemas(min_cinemas, films_in_many_cinemas)
    output_movies_to_console(movies_in_cinemas, films_needed)
