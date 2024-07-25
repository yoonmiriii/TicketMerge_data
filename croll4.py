from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import time
import csv

def scroll_into_view(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(2)  # 스크롤 후 대기

def get_additional_elements(driver):
    try:
        # 추가된 공연 링크들 가져오기
        new_elements = driver.find_elements(By.XPATH, '//*[@id="perf_poster"]/li')
        return new_elements
    except StaleElementReferenceException as se:
        print(f"Stale element reference: {str(se)}")
        return []

# 웹 드라이버 설정
def initialize_driver():
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)
# 웹 드라이버 초기화
driver = initialize_driver()

# URL 설정
url = 'https://ticket.melon.com/concert/index.htm?genreType=GENRE_CON'

# 웹 페이지 열기
driver.get(url)
driver.maximize_window()

# WebDriverWait를 사용하여 공연 리스트가 로드될 때까지 기다림 (10초로 설정)
wait = WebDriverWait(driver, 10)



try:
    
    # 초기화
    elements = []

    # 최초의 공연 링크들 가져오기
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#perf_poster > li')))

    # CSV 파일 설정
    with open('data.csv', mode='w', newline='', encoding='utf-8') as data_file, open('artist.csv', mode='w', newline='', encoding='utf-8') as artist_file:
        data_writer = csv.writer(data_file)
        artist_writer = csv.writer(artist_file)

        # CSV 파일 헤더 작성
        data_writer.writerow(["상품 제목", "포스터 URL", "상세 포스터 URL", "공연장소", "공연기간", "캐스팅 리스트"])
        artist_writer.writerow(["이름", "URL"])

        processed_elements = set()  # 처리된 요소들을 추적하기 위한 집합

        # 공연 리스트 링크 순회
        while elements:
            element = elements.pop(0)  # 리스트의 첫 번째 요소 가져오기

            # 이미 처리된 요소는 건너뜀
            if element in processed_elements:
                continue

            try:
                # 요소로 스크롤
                scroll_into_view(driver, element)

                # 공연 링크 클릭
                element.click()

                # WebDriverWait를 사용하여 페이지가 완전히 로드될 때까지 기다림
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.box_consert_thumb')))

                # 페이지 소스 가져오기
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')

                # 상품 제목 가져오기
                product_title = soup.select_one('p.tit').get_text(strip=True)
                print(f"상품 제목: {product_title}")

                # 포스터 URL 가져오기
                poster_url = soup.select_one('div.box_consert_thumb img')['src']
                print(f"포스터 URL: {poster_url}")

                # 상세 포스터 URL 가져오기
                detail_poster_element = soup.select_one('div.box_img_content img')
                if detail_poster_element:
                    detail_poster_url = detail_poster_element['src']
                    print(f"상세 포스터 URL: {detail_poster_url}")
                else:
                    print("상세 포스터 URL을 찾을 수 없습니다.")

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

                # CSV 파일에 데이터 추가
                cast_names = [casting["이름"] for casting in casting_list]
                data_writer.writerow([product_title, poster_url,detail_poster_url,place,performance_date,cast_names])

                for casting in casting_list:
                    artist_writer.writerow ([casting["이름"], casting["프로필 이미지 URL"]])

                # 현재 요소를 처리된 요소로 추가
                processed_elements.add(element)
                # 뒤로가기
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
                
            finally:
                try:
                    driver.refresh()
                    
                    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#perf_poster > li')))

                    # 추가 데이터 가져오기
                    new_elements = get_additional_elements(driver)
                    new_elements = [el for el in new_elements if el not in processed_elements and el not in elements]  # 기존 요소 및 처리된 요소 제외
                    elements.extend(new_elements)
                    time.sleep(2)
                    


                except StaleElementReferenceException as se:
                    print(f"Stale element reference: {str(se)}")
                except Exception as e:
                    print(f"An error occurred: {str(e)}")

except TimeoutException as te:
    print(f"Timeout occurred: {str(te)}")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    # 브라우저 닫기
    driver.quit()

print("크롤링이 완료되었습니다.")