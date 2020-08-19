import requests
from bs4 import BeautifulSoup
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')
movies = soup.select('#tbody_0 > tr')
# #contents > div.wrap-movie-chart > div.sect-movie-chart > ol:nth-child(2) > li:nth-child(1) > div.box-contents > div > div > span.percent
print(movies)
for movie in movies:
    rank = movie.select_one('td.tal >span.ellip.per90 > a').text
    print(rank)