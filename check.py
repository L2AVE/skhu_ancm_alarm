import re # 정규식
import requests
import json
import time
from bs4 import BeautifulSoup




def total_check():
    # 게시판 form에 있는 주소를 가져옴
    html = requests.get('https://www.skhu.ac.kr/bbs/skhu/32/artclList.do')
    #html = requests.get('https://cafe.naver.com/nsollll')
    
    soup = BeautifulSoup(html.text, 'html.parser')

    # 전체 게시글 수 파싱
    total = soup.select('body > div > form:nth-child(1) > div.board-rss > div > p > strong')
    #total = soup.select('#cafe-menu > div.box-g-m > ul > li > span')

    # 숫자 뽑기 정규식
    total = re.sub(r'[^0-9]', '', str(total))
    return total


#https://kauth.kakao.com/oauth/authorize?client_id=65b126bbb86cdc90b1a972f905f4f4b6&redirect_uri=https://localhost:3000&response_type=code&scope=talk_message


url = 'https://kauth.kakao.com/oauth/token'  
rest_api_key = '65b126bbb86cdc90b1a972f905f4f4b6'  
redirect_uri = 'https://localhost:3000'  
authorize_code = 'yBwRFRCESyOvFXRCnRGV2Sd4TrY9jG6oI7Lsk4a_VGnCjy5CfdPFhgNaJ0ybGnXCz8dwtAo9cpgAAAGI2jxGFg'  

def f_auth():
    data = {
        'grant_type': 'authorization_code',
        'client_id': rest_api_key,
        'redirect_uri': redirect_uri,
        'code': authorize_code
    }

    response = requests.post(url, data=data)
    tokens = response.json()

    with open("kakao_code.json", "w") as fp:
        json.dump(tokens, fp)
    with open("kakao_code.json", "r") as fp:
        ts = json.load(fp)
    r_token = ts["refresh_token"]
    return r_token


def f_auth_refresh(r_token):
    with open("kakao_code.json", "r") as fp:
        ts = json.load(fp)
    data = {
        "grant_type": "refresh_token",
        "client_id": rest_api_key,
        "refresh_token": r_token
    }
    response = requests.post(url, data=data)
    tokens = response.json()

    with open(r"kakao_code.json", "w") as fp:
        json.dump(tokens, fp)
    with open("kakao_code.json", "r") as fp:
        ts = json.load(fp)
    token = ts["access_token"]
    return token



# 1시간마다 total_check 호출 해서 값이 1시간 전 total 보다 크면 게시글이 올라온 것으로 판단

    
def f_send_talk(token, text):
    header = {'Authorization': 'Bearer ' + token}
    url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'  
    post = {
        'object_type': 'text',
        'text': text,
        'link': {
            'web_url': 'https://www.skhu.ac.kr/skhu/1041/subview.do',
            'mobile_web_url': 'https://www.skhu.ac.kr/skhu/1041/subview.do'
        },
        'button_title': '바로가기'
    }
    data = {'template_object': json.dumps(post)}
    return requests.post(url, headers=header, data=data)


r_token = f_auth()


while True:
    token = f_auth_refresh(r_token)
    total = total_check()
    # 1시간마다 전체글 수 체크
    time.sleep(3600)
    # 1시간 전 글수와 비교해서 지금 글 수가 많으면 게시글 올라온 것으로 판단
    if(total < total_check()):
        f_send_talk (token, '학점 교류 시작!')
        # 메시지가 발송되면 1달 sleep 걸고 다음 공지 대기
        time.sleep(2592000)
    
    