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
    return jsonify({'movies': movies, 'result': "success"})

@app.route('/cgv', methos=['POST'])
def from_cgv():
    rank1 = requests.form['rank[0]']
    rank2 = requests.form['rank[1]']
    rank3 = requests.form['rank[2]']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('http://www.cgv.co.kr/movies/', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    crawl_info =soup.select_one('#contents > div.wrap-movie-chart > div.sect-movie-chart')
    first_ol_info = crawl_info.select_one('ol:nthchild(2) > li')
    for infos in first_ol_info :
        percent = infos.select_one('div.box-contents > div > div > span.percent')


            # #contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2) > li:nth-child(1) > div.box-contents > div > div
            ##contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2)
            ##contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2) > li:nth-child(1) > div.box-contents > div > div > span.percent


if __name__ == '__main__':
    app.run('0.0.0.0', port=5005, debug=True)