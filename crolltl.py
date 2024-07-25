
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
url = 'https://www.ticketlink.co.kr/product/50125'

# 웹 페이지 열기
driver.get(url)
driver.maximize_window()

time.sleep(10)

# 페이지 소스 가져오기
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 해당 링크 가져오기
current_url = driver.current_url
print("URL:", current_url)

# 상품 제목 가져오기
title = soup.select_one('h1.product_title').get_text(strip=True)
print(f"상품 제목: {title}")

# 포스터 URL 가져오기
poster_url = "https:" + soup.select_one('div.product_detail_imgbox img')['src']
print(f"포스터 URL: {poster_url}")


# 상세 포스터 URL 가져오기
try:
    detail_poster_url = ""
    artwork_images = []

    # 첫 번째 시도: div.product_templete img
    detail_poster_element = soup.select_one('div.product_templete img')
    if detail_poster_element:
        detail_poster_url = detail_poster_element['src']
        print(f"상세 포스터 URL: {detail_poster_url}")
    else:
        print("첫 번째 상세 포스터 URL을 찾을 수 없습니다.")

    # 두 번째 시도: div.product_templete p img
    if not detail_poster_url:
        detail_poster_element = soup.select_one('div.product_templete p img')
        if detail_poster_element:
            detail_poster_url = detail_poster_element['src']
            print(f"상세 포스터 URL: {detail_poster_url}")
        else:
            print("두 번째 상세 포스터 URL을 찾을 수 없습니다.")

    # 세 번째 시도: div.product_templete a img (상세 포스터 URL이 없을 경우에만)
    if not detail_poster_url:
        artwork_elements = soup.select('div.product_templete a img')
        if artwork_elements:
            for artwork in artwork_elements:
                artwork_images.append(artwork['src'])
            print(f"작품 설명 이미지: {artwork_images}")

            # 작품 설명 이미지를 쉼표로 구분된 하나의 문자열로 변환하여 detail_poster_url에 저장
            if artwork_images:
                detail_poster_url = ', '.join(artwork_images)
                print(f"변환된 상세 포스터 URL: {detail_poster_url}")
        else:
            print("작품 설명 이미지를 찾을 수 없습니다.")

    # 네 번째 시도: div.product_templete img (상세 포스터 URL이 없을 경우에만)
    if not detail_poster_url:
        artwork_elements = soup.select('div.product_templete img')
        if artwork_elements:
            for artwork in artwork_elements:
                artwork_images.append(artwork['src'])
            print(f"작품 설명 이미지: {artwork_images}")

            # 작품 설명 이미지를 쉼표로 구분된 하나의 문자열로 변환하여 detail_poster_url에 저장
            if artwork_images:
                detail_poster_url = ', '.join(artwork_images)
                print(f"변환된 상세 포스터 URL: {detail_poster_url}")
        else:
            print("작품 설명 이미지를 찾을 수 없습니다.")
except Exception as e:
    print(f"An error occurred while fetching detail poster URL: {str(e)}")

# # 공연 장소와 기간 가져오기
try:
    # 공연 장소 가져오기
    place_element = soup.select_one('ul.product_info_list.type_col2 li.product_info_item:nth-of-type(1) div.product_info_desc')
    if place_element:
        place = place_element.get_text(strip=True)
        print(f"공연 장소: {place}")
    else:
        print("공연 장소를 찾을 수 없습니다.")

    # 공연 기간 가져오기
    performance_date_element = soup.select_one('ul.product_info_list.type_col2 li.product_info_item:nth-of-type(3) div.product_info_desc')
    if performance_date_element:
        date = performance_date_element.get_text(strip=True).replace("\n", "").replace(" ", "")
        print(f"공연 기간: {date}")
    else:
        print("공연 기간을 찾을 수 없습니다.")
except Exception as e:
    print(f"An error occurred while fetching place and performance date: {str(e)}")

# 주연 이름 리스트 가져오기
try:
    main_cast_list = []

    # "주연" 항목의 td 요소 선택
    cast_element = soup.select_one('tbody tr:has(th[scope="row"]:contains("주연")) td')

    if cast_element:
        # 주연 이름들을 쉼표로 구분하여 리스트로 저장
        cast_list = [name.strip() for name in cast_element.get_text(strip=True).split(',')]
        print(f"주연: {cast_list}")
    else:
        print("주연 항목을 찾을 수 없습니다.")
except Exception as e:
    print(f"An error occurred while fetching main cast: {str(e)}")

# 브라우저 닫기
driver.quit()

# CSV 파일로 저장
with open('data2.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    
    writer.writerow(["상품 제목","포스터 URL","상세 포스터 URL", "공연장소","공연기간","캐스팅 리스트", "해당링크"])
    writer.writerow([title,poster_url,detail_poster_url,place,date,main_cast_list,current_url])
print("CSV 파일로 저장이 완료되었습니다.")

