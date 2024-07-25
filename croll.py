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
url = 'https://tickets.interpark.com/goods/24002093'

# 웹 페이지 열기
driver.get(url)

time.sleep(10)

# 페이지 소스 가져오기
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 상품 제목, 서브 제목 가져오기 - 서브제목 필요없으니 삭제
title = soup.select_one('.prdTitle').get_text(strip=True)
print(f"상품 제목: {title}")

# 썸네일 URL
thumbnail_URL = "http:" + soup.select_one('.posterBox .posterBoxTop img')['src']
print(f"포스터 URL: {thumbnail_URL}")

# 상세포스터 URL
content_detail_images = soup.select('div.contentDetail img')
detail_image_URL = ["https:" + img['src'] for img in content_detail_images]
print(detail_image_URL)

# 공연장소
place = soup.select_one('.infoBtn').get_text(strip=True)
print(f"공연장소: {place}")

# 공연기간
date = soup.select_one('.infoText').get_text(strip=True)
print(f"공연기간: {date}")


# 캐스팅 리스트 가져오기
castings = soup.select('ul.castingList li.castingItem')
casting_data = []
for idx, casting in enumerate(castings, start=1):
    profile_image = "https:" + casting.select_one('div.castingProfile img')['src']  # 이미지 URL 가져오기
    name = casting.select_one('div.castingName').get_text(strip=True)  # 이름 가져오기
    print(f"{idx}. 이름: {name}, 프로필 이미지 URL: {profile_image}")
    casting_data.append({"이름": name, "프로필 이미지 URL": profile_image})
# 브라우저 닫기
driver.quit()

# CSV 파일로 저장
with open('data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # 기본 정보 작성
    casting_list = []
    for idx, casting in enumerate(casting_data, start=1):
        casting_list.append(casting["이름"])
    writer.writerow(["상품 제목","포스터 URL","상세 포스터 URL", "공연장소","공연기간","캐스팅 리스트"])
    writer.writerow([title,thumbnail_URL,", ".join(detail_image_URL),place,date,casting_list])
print("CSV 파일로 저장이 완료되었습니다.")

with open('artist.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["이름", "URL"])
    for casting in casting_data:
        writer.writerow([casting["이름"], casting["프로필 이미지 URL"]])

print("CSV 파일로 저장이 완료되었습니다.")