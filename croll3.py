from pandas import notnull
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv

# 웹 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# URL 설정
url = 'https://ticket.melon.com/performance/index.htm?prodId=210034'

# 웹 페이지 열기
driver.get(url)
driver.maximize_window()

time.sleep(10)

# 페이지 소스 가져오기
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 상품 제목 가져오기
product_title = soup.select_one('p.tit').get_text(strip=True)
print(f"상품 제목: {product_title}")

# 포스터 URL 가져오기
poster_url = soup.select_one('div.box_consert_thumb img')['src']
print(f"포스터 URL: {poster_url}")


# 상세 포스터 URL 및 작품 설명 이미지 가져오기
detail_poster_url = ''
artwork_images = []

# 상세 포스터 URL 가져오기        
detail_poster_element = soup.select_one('div.box_img_content img')
if detail_poster_element:
    detail_poster_url = detail_poster_element['src']
    print(f"상세 포스터 URL: {detail_poster_url}")
else:
    print("상세 포스터 URL을 찾을 수 없습니다.")

detail_poster_element = soup.select_one('div.box_img_content p img')
if detail_poster_element:
    detail_poster_url = detail_poster_element['src']
    print(f"상세 포스터 URL: {detail_poster_url}")
else:
    print("상세 포스터 URL을 찾을 수 없습니다.")

# 작품 설명 이미지 가져오기 (상세 포스터 URL이 없을 경우에만)
if not detail_poster_url:
    artwork_elements = soup.select('div.box_img_content a img')
    for artwork in artwork_elements:
        artwork_images.append(artwork['src'])
    print(f"작품 설명 이미지: {artwork_images}")

    # 작품 설명 이미지를 쉼표로 구분된 하나의 문자열로 변환하여 detail_poster_url에 저장
    if artwork_images:
        detail_poster_url = ', '.join(artwork_images)
        print(f"변환된 상세 포스터 URL: {detail_poster_url}")

# 공연 장소 가져오기
place = soup.select_one('dd.txt_info a#performanceHallBtn span.place').get_text(strip=True)
print(f"공연 장소: {place}")

# 공연 기간 가져오기
performance_date = soup.select_one('dd#periodInfo').get_text(strip=True)
print(f"공연 기간: {performance_date}")

# 캐스팅 리스트 가져오기
casting_list = []
artists = soup.select('ul.list_artist li')
for artist in artists:
    name_tag = artist.select_one('a.txt_name strong.singer')
    if name_tag:  # name_tag가 존재하는 경우에만 실행
        name = name_tag.text.strip()
        if name:  # name이 비어 있지 않은 경우에만 실행
            image_url = artist.select_one('span.thumb img')['src']
            casting_list.append({'이름': name, '프로필 이미지 URL': image_url})

print(casting_list)

# 브라우저 닫기
driver.quit()

# CSV 파일로 저장
with open('data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # 기본 정보 작성
    cs = []
    for idx, casting in enumerate(casting_list, start=1):
        cs.append(casting["이름"])
    writer.writerow(["상품 제목","포스터 URL","상세 포스터 URL", "공연장소","공연기간","캐스팅 리스트"])
    writer.writerow([product_title,poster_url,detail_poster_url,place,performance_date,cs])
print("CSV 파일로 저장이 완료되었습니다.")

with open('artist.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["이름", "URL"])
    for casting in casting_list:
        writer.writerow([casting["이름"], casting["프로필 이미지 URL"]])

print("CSV 파일로 저장이 완료되었습니다.")