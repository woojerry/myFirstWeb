from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver

app = Flask(__name__)

client = MongoClient('mongodb://test:test@localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.dbsparta


@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/date', methods=['POST'])
# def get_Date() :
#      date_from_button = request.form['datepicker1']
#      print(date_from_button)


@app.route('/box_office', methods=['GET'])
def box_office():
    response = requests.get('http://www.kobis.or.kr/kobis/business/main/searchMainDailyBoxOffice.do')
    movies = response.json()

    #기준일
    date = movies[0]['endDate'] #YYYY.MM.DD
    date_for_calendar = movies[0]['showDt'] #YYYYMMDD

    #영화랭킹 Top3
    rank1 = movies[0]['movieNm']
    rank2 = movies[1]['movieNm']
    rank3 = movies[2]['movieNm']

    #영화 개봉일
    rank1_opendt = ''
    rank2_opendt = ''
    rank3_opendt = ''

    #골든에그지수
    rank1_percent = 0
    rank2_percent = 0
    rank3_percent = 0

    #네이버평점
    rank1_score = 0
    rank2_score = 0
    rank3_score = 0

    #네이버 가져오는 포스터
    rank1_poster = ''
    rank2_poster = ''
    rank3_poster = ''

    #영화감독
    rank1_director = ''
    rank2_director = ''
    rank3_director = ''

    #출연배우
    rank1_actors =[]
    rank2_actors = []
    rank3_actors = []

    #누적관객수
    rank1_attendance = ''
    rank2_attendance = ''
    rank3_attendance = ''

    #왓챠 평점
    rank1_wscore = 0
    rank2_wscore = 0
    rank3_wscore = 0

    #crawl from CGV
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('http://www.cgv.co.kr/movies/?lt=1&ft=1', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')

    crawl_info =soup.select_one('#contents > div.wrap-movie-chart > div.sect-movie-chart')
    #첫번째 ol태그에서 정보 가져오기
    ##contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2) > li:nth-child(2) > div.box-contents > div > div > span.percent
    ##contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2)
    ##contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2) > li:nth-child(1) > div.box-contents > a > strong
    first_ol_info = crawl_info.select('ol:nth-child(2) > li')
    for infos in first_ol_info :
        movie_name = infos.select_one('div.box-contents > a > strong').text
        movie_name = movie_name.replace("-", ": ") #if : 오면 -> - 로 바꿔주기 !
        percent = infos.select_one('div.box-contents > div > div > span.percent').text
        movie_opendt = infos.select_one('div.box-contents > span.txt-info > strong').text.strip().split("개")[0].strip()

        if movie_name == rank1 :
            rank1_percent = percent
            rank1_opendt = movie_opendt
        elif movie_name == rank2 :
            rank2_percent = percent
            rank2_opendt = movie_opendt
        elif movie_name == rank3 :
            rank3_percent = percent
            rank3_opendt = movie_opendt

    #두번째 ol태그에서 정보 가져오기
    second_ol_info = crawl_info.select('ol:nth-child(3) > li')
    for infos in second_ol_info :
        movie_name = infos.select_one('div.box-contents > a > strong').text
        movie_name = movie_name.replace("-", ": ")
        percent = infos.select_one('div.box-contents > div > div > span.percent').text
        movie_opendt = infos.select_one('div.box-contents > span.txt-info > strong').text.strip().split("개")[0].strip()
        if movie_name == rank1 :
            rank1_percent = percent
            rank1_opendt = movie_opendt
        elif movie_name == rank2 :
            rank2_percent = percent
            rank2_opendt = movie_opendt
        elif movie_name == rank3 :
            rank3_percent = percent
            rank3_opendt = movie_opendt

    #crawl_from_Naver
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://movie.naver.com/movie/running/current.nhn', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    crawl_infos = soup.select('#content > div.article > div:nth-child(1) > div.lst_wrap > ul > li')
    for crawl_info in crawl_infos[0:5]:
        movie_name = crawl_info.select_one('dl > dt > a').text
        naver_score = crawl_info.select_one('dl > dd.star > dl.info_star > dd > div > a > span.num').text
        movie_poster = crawl_info.select_one('div > a > img')['src'].split('?')[0] #포스터 화질 개선을 위해 뒷부분 split
        movie_director = crawl_info.select_one('dl > dd:nth-child(3) > dl > dd:nth-child(4) > span > a').text
        actors = crawl_info.select('dl > dd:nth-child(3) > dl > dd:nth-child(6) > span > a')
        movie_actor = []
        for i in actors:
            actor = i.text
            movie_actor.append(actor)

        if movie_name == rank1 :
            rank1_score = naver_score
            rank1_poster = movie_poster
            rank1_director = movie_director
            rank1_actors = movie_actor
        elif movie_name == rank2 :
            rank2_score = naver_score
            rank2_poster = movie_poster
            rank2_director = movie_director
            rank2_actors = movie_actor
        elif movie_name == rank3 :
            rank3_score = naver_score
            rank3_poster = movie_poster
            rank3_director = movie_director
            rank3_actors = movie_actor

    # crawl_from_WATCHA PEDIA by selenium
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('lang=ko_KR')

    driver = webdriver.Chrome('/home/ubuntu/my_project/chromedriver', chrome_options=chrome_options)
                                 # 디버깅 시 -> chromedriver.exe 배포시에는 -> /home/ubuntu/my_project/chromedriver
    driver.implicitly_wait(1)
    driver.get('https://pedia.watcha.com/ko-KR')

    # chrome.find_element_by_css_selector('')
    source = driver.page_source
    soup = BeautifulSoup(source, 'html.parser')

    # Linux Watcha ver.
    crawl_from_watcha = soup.select(
        'ul.ebeya3l0.css-wvdjot-VisualUl-StyledHorizontalUl-StyledHorizontalUlWithContentPosterList-RowList.eykn4p10>li')
    for infos in crawl_from_watcha[0:5]:
        movie_name = infos.select_one('a > div > div.css-1teivyt-ContentTitle.e3fgkal3').text
        movie_attendance = infos.select_one('a > div > div.css-hyqnp8-StyledContentBoxOfficeStats.ebeya3l13').text.strip().split('・')[1]
        watcha_score = infos.select_one('a > div > div> span:nth-child(3)').text

    # Windows Watcha ver.
    # crawl_from_watcha = soup.select('#root > div > div.css-1sh3zvx-NavContainer.ebsyszu0 > section > div > section > div:nth-child(1) >'
    #                                 ' div.css-gc1vu8-StyledHorizontalScrollOuterContainer.ebeya3l4 > div > div.css-chidac-ScrollBar.e1f5xhlb1 > div > div > ul > li')
    # for infos in crawl_from_watcha[0:4]:
    #     movie_name = infos.select_one('a > div.css-dmreg0-ContentInfo.e3fgkal2 > div.css-1teivyt-ContentTitle.e3fgkal3').text
    #     movie_attendance = infos.select_one('a > div > div.css-hyqnp8-StyledContentBoxOfficeStats.ebeya3l13').text.strip().split('・')[1]
    #     watcha_score = infos.select_one('a > div.css-dmreg0-ContentInfo.e3fgkal2 > div.average.css-uaqea0-ContentRating-StyledContentRating.ebeya3l14 > span:nth-child(3)').text

        if movie_name == rank1:
            rank1_attendance = movie_attendance
            rank1_wscore = watcha_score
        elif movie_name == rank2:
            rank2_attendance = movie_attendance
            rank2_wscore = watcha_score
        elif movie_name == rank3:
            rank3_attendance = movie_attendance
            rank3_wscore = watcha_score
    driver.quit()

    movie_infos = {
        'KOBIS':{
            'date' : date,
            'rank1_infos' :{
                'rank1': rank1,
            },
            'rank2_infos': {
                'rank2': rank2,
            },
            'rank3_infos': {
                'rank3': rank3,
            }
        },
        'CGV':{
            'rank1_infos' :{
                'goldenegg1' : rank1_percent,
                'openDt1': rank1_opendt
            },
            'rank2_infos' :{
                'goldenegg2' : rank2_percent,
                'openDt2': rank2_opendt
            },
            'rank3_infos' :{
                'goldenegg3' : rank3_percent,
                'openDt3': rank3_opendt
            }
        },
        'Naver':{
            'rank1_infos' :{
                'naverscore1' : rank1_score,
                'poster1' : rank1_poster,
                'director1' : rank1_director,
                'actors1' : rank1_actors
            },
            'rank2_infos': {
                'naverscore2': rank2_score,
                'poster2': rank2_poster,
                'director2': rank2_director,
                'actors2' : rank2_actors,
            },
            'rank3_infos' :{
                'naverscore3' : rank3_score,
                'poster3' : rank3_poster,
                'director3': rank3_director,
                'actors3' : rank3_actors
            },
        },
        'Watcha':{
            'rank1_infos' :{
                'wscore1' : rank1_wscore,
                'att1': rank1_attendance
            },
            'rank2_infos' :{
                'wscore2' : rank2_wscore,
                'att2': rank2_attendance
            },
            'rank3_infos' :{
                'wscore3' : rank3_wscore,
                'att3': rank3_attendance
            }
        }
    }
    #db.myproject.insert_one(movie_infos)
    return jsonify({'result': 'success', 'movie_infos' : movie_infos})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)