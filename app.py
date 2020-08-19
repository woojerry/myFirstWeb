from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/kobis', methods=['GET'])
def read_kobis():
    response = requests.get('http://www.kobis.or.kr/kobis/business/main/searchMainDailyBoxOffice.do')
    movies = response.json()
 #   movie_title = movies[0]['movieNm']
 #   print(movie_title)
    # response에서 하는법으로 하는게 나은지?
    return jsonify({'movies': movies, 'result': "success"})

@app.route('/cgv', methods=['GET'])
def from_cgv():
    response = requests.get('http://www.kobis.or.kr/kobis/business/main/searchMainDailyBoxOffice.do')
    movies = response.json()

    #영화랭킹 Top3
    rank1 = movies[0]['movieNm']
    rank2 = movies[1]['movieNm']
    rank3 = movies[2]['movieNm']

    #골든에그지수
    rank1_percent = 0
    rank2_percent = 0
    rank3_percent = 0


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('http://www.cgv.co.kr/movies', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    crawl_info =soup.select_one('#contents > div.wrap-movie-chart > div.sect-movie-chart')
    #첫번째 ol태그에서 정보 가져오기
    ##contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2) > li:nth-child(2) > div.box-contents > div > div > span.percent
    ##contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2)
    ##contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2) > li:nth-child(1) > div.box-contents > a > strong
    first_ol_info = crawl_info.select('ol:nth-child(2) > li')
    for infos in first_ol_info :
        movie_name = infos.select_one('div.box-contents > a > strong').text
        percent = infos.select_one('div.box-contents > div > div > span.percent').text
        if movie_name == rank1 :
            rank1_percent = percent
        elif movie_name == rank2 :
            rank2_percent = percent
        elif movie_name == rank3 :
            rank3_percent = percent

    #두번째 ol태그에서 정보 가져오기
    second_ol_info = crawl_info.select('ol:nth-child(3) > li')
    for infos in second_ol_info :
        movie_name = infos.select_one('div.box-contents > a > strong').text
        percent = infos.select_one('div.box-contents > div > div > span.percent').text
        if movie_name == rank1 :
            rank1_percent = percent
        elif movie_name == rank2 :
            rank2_percent = percent
        elif movie_name == rank3 :
            rank3_percent = percent

    movie_infos = {
        'rank1_m' : rank1,
        'rank2_m' : rank2,
        'rank3_m' : rank3,
        'rank1_p' : rank1_percent,
        'rank2_p' : rank2_percent,
        'rank3_p' : rank3_percent
    }
    db.myproject.insert_one(movie_infos)
    return jsonify({'result': 'success'})

@app.route('/naver', methods=['GET'])
def from_naver():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://movie.naver.com/movie/running/current.nhn', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    crawl_infos = soup.select('#content > div.article > div:nth-child(1) > div.lst_wrap > ul')


 ##content > div.article > div:nth-child(1) > div.lst_wrap > ul > li:nth-child(1)





if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)