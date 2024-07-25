from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import csv

# 웹 드라이버 설정
def initialize_driver():
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)

# 웹 페이지에서 공연 정보를 가져오는 함수
def scrape_performance_info(driver, element):
    try:
        # 요소로 스크롤
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)  # 스크롤 후 대기

        # 요소 클릭하여 링크 열기
        element.click()

        # 대기 시간
        time.sleep(3)

        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # 해당 링크 가져오기
        current_url = driver.current_url
        print("URL:", current_url)

        # 상품 제목 가져오기
        title = soup.select_one('div.product_heading h1.product_title').get_text(strip=True)
        print(f"상품 제목: {title}")

        # 포스터 URL 가져오기
        poster_url = "https:" + soup.select_one('div.product_detail_imgbox img')['src']
        print(f"포스터 URL: {poster_url}")

        # 상세 포스터 URL 및 작품 설명 이미지 가져오기
        detail_poster_url = ''
        artwork_images = []

        try:
            # 상세 포스터 URL 가져오기 시도
            detail_poster_element = soup.select_one('div.product_templete img')
            if detail_poster_element:
                detail_poster_url = detail_poster_element['src']
                print(f"상세 포스터 URL: {detail_poster_url}")
            else:
                print("상세 포스터 URL을 찾을 수 없습니다.")

            # 작품 설명 이미지 가져오기 시도
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

        except Exception as e:
            print(f"An error occurred while fetching detail poster URL: {str(e)}")

        # 공연 장소 가져오기
        place = soup.select_one('ul.product_info_list.type_col2 li.product_info_item:nth-of-type(1) div.product_info_desc').get_text(strip=True)
        print(f"공연 장소: {place}")

        # 공연 기간 가져오기
        date = soup.select_one('ul.product_info_list.type_col2 li.product_info_item:nth-of-type(3) div.product_info_desc').get_text(strip=True).replace("\n", "").replace(" ", "")
        print(f"공연 기간: {date}")

        # 주연 이름 리스트 가져오기
        main_cast_list = []
        try:
            main_cast_element = soup.select_one('tbody tr:has(th[scope="row"]:contains("주연")) td')
            if main_cast_element:
                casting_list = [name.strip() for name in main_cast_element.get_text(strip=True).split(',')]
        except Exception as e:
            print(f"An error occurred while fetching main cast: {str(e)}")
        print(f"주연: {main_cast_list}")

        # CSV 파일에 데이터 추가
        with open('ticketlink_data.csv', mode='a', newline='', encoding='utf-8') as data_file:
            data_writer = csv.writer(data_file)
            data_writer.writerow([title, poster_url, detail_poster_url, place, date, casting_list, current_url])

        # 원래 페이지로 돌아가기 (뒤로 가기)
        driver.back()
        time.sleep(2)

    except TimeoutException as te:
        print(f"Timeout occurred: {str(te)}")
    except NoSuchElementException as nse:
        print(f"Element not found: {str(nse)}")
    except StaleElementReferenceException as se:
        print(f"Stale element reference: {str(se)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# 웹 드라이버 초기화
driver = initialize_driver()

# URL 설정
url = 'https://www.ticketlink.co.kr/performance/14'

# 웹 페이지 열기
driver.get(url)
driver.maximize_window()

# WebDriverWait를 사용하여 공연 리스트가 로드될 때까지 기다림 (10초로 설정)
wait = WebDriverWait(driver, 10)

try:
    # 페이지를 여러 번 아래로 내리기
    for _ in range(30):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)  # 스크롤 후 대기

    # 페이지를 위로 올리기
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.HOME)
    time.sleep(1)  # 스크롤 후 대기

    # 페이지를 여러 번 아래로 내리기
    for _ in range(4):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)  # 스크롤 후 대기

    time.sleep(3)

    # 초기화
    elements = []

    # 최초의 공연 링크들 가져오기
    elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content"]/section[5]/div/div[3]/ul/li')))

    # CSV 파일 설정
    with open('ticketlink_data.csv', mode='w', newline='', encoding='utf-8') as data_file:
        data_writer = csv.writer(data_file)
        data_writer.writerow(["상품 제목", "포스터 URL", "상세 포스터 URL", "공연장소", "공연기간", "캐스팅 리스트", "해당 링크"])

        processed_elements = set()  # 처리된 요소들을 추적하기 위한 집합

        # 공연 리스트 링크 순회
        for x in range(1, 131):  # y가 1에서 130까지 증가 (총 130개)
            # XPath 경로 설정
            path = f'//*[@id="content"]/section[5]/div/div[3]/ul/li[{x}]'

            try:
                # 해당 요소 찾기
                element = driver.find_element(By.XPATH, path)

                # 이미 처리된 요소는 건너뜀
                if element in processed_elements:
                    continue

                # 현재 탭에서 링크 클릭 및 작업 수행
                scrape_performance_info(driver, element)

                # 현재 요소를 처리된 요소로 추가
                processed_elements.add(element)

                time.sleep(2)

            except NoSuchElementException:
                print(f"경로 {path}에서 요소를 찾을 수 없습니다.")
            except Exception as e:
                print(f"에러 발생: {str(e)}")
                continue

except TimeoutException as te:
    print(f"Timeout occurred: {str(te)}")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    # 브라우저 닫기
    driver.quit()

print("크롤링이 완료되었습니다.")
