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

def get_additional_elements():
    try:
        # 추가된 공연 링크들 가져오기
        new_elements = driver.find_elements(By.XPATH, '//*[@id="contents"]/article[5]/section/div[2]/div[2]/a')
        return new_elements
    except StaleElementReferenceException as se:
        print(f"Stale element reference: {str(se)}")
        return []

# 웹 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# URL 설정
url = 'https://tickets.interpark.com/contents/genre/concert'

# 웹 페이지 열기
driver.get(url)
driver.maximize_window()

# WebDriverWait를 사용하여 공연 리스트가 로드될 때까지 기다림 (10초로 설정)
wait = WebDriverWait(driver, 10)



try:
    # 페이지를 여러 번 아래로 내리기
    for _ in range(3):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(1)  # 스크롤 후 대기
    
    # '전체 공연 보기' 버튼 클릭
    btnAll = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/article[5]/section/div[2]/div[1]/div/button[1]')))
    btnAll.click()
    
    # 초기화
    elements = []

    # 최초의 공연 링크들 가져오기
    elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="contents"]/article[5]/section/div[2]/div[2]/a')))

    # CSV 파일 설정
    with open('intepark_data.csv', mode='w', newline='', encoding='utf-8') as data_file, open('interpark_artist.csv', mode='w', newline='', encoding='utf-8') as artist_file:
        data_writer = csv.writer(data_file)
        artist_writer = csv.writer(artist_file)

        # CSV 파일 헤더 작성
        data_writer.writerow(["제목", "포스터 URL", "상세 포스터 URL", "공연장소", "공연기간", "캐스팅 리스트","해당 링크"])
        artist_writer.writerow(["이름", "프로필 이미지 URL"])

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

                # 탭 전환
                driver.switch_to.window(driver.window_handles[-1])  # 가장 최근에 열린 탭으로 전환

                # WebDriverWait를 사용하여 페이지가 완전히 로드될 때까지 기다림
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.prdTitle')))

                # 페이지 소스 가져오기
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                
                # 해당 링크 가져오기
                current_url = driver.current_url
                print("URL:", current_url)

                # 상품 제목, 서브 제목 가져오기
                title = soup.select_one('.prdTitle').get_text(strip=True)

                # 포스터 URL
                thumbnail_URL = "http:" + soup.select_one('.posterBox .posterBoxTop img')['src']

                # 상세포스터 URL
                content_detail_images = soup.select('div.contentDetail img')
                detail_image_URL = ["https:" + img['src'] for img in content_detail_images]

                # 공연장소
                place = soup.select_one('.infoBtn').get_text(strip=True)

                # 공연기간
                date = soup.select_one('.infoText').get_text(strip=True)

                # 캐스팅 리스트 가져오기
                castings = soup.select('ul.castingList li.castingItem')
                casting_data = [{"이름": casting.select_one('div.castingName').get_text(strip=True),
                                 "프로필 이미지 URL": "https:" + casting.select_one('div.castingProfile img')['src']} for casting in castings]

                # CSV 파일에 데이터 추가
                casting_list = [casting["이름"] for casting in casting_data]
                data_writer.writerow([title, thumbnail_URL, ", ".join(detail_image_URL), place, date, ", ".join(casting_list), current_url])

                for casting in casting_data:
                    artist_writer.writerow([casting["이름"], casting["프로필 이미지 URL"]])

                # 현재 요소를 처리된 요소로 추가
                processed_elements.add(element)

            except TimeoutException as te:
                print(f"Timeout occurred: {str(te)}")
                driver.refresh()
            except NoSuchElementException as nse:
                print(f"Element not found: {str(nse)}")
                driver.refresh()
            except StaleElementReferenceException as se:
                print(f"Stale element reference: {str(se)}")
                driver.refresh()
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                driver.refresh()
            finally:
                try:
                    # 탭 닫기 및 원래 탭으로 전환
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)  # 탭 전환 후 대기

                    # 추가 데이터 가져오기
                    new_elements = get_additional_elements()
                    new_elements = [el for el in new_elements if el not in processed_elements and el not in elements]  # 기존 요소 및 처리된 요소 제외
                    elements.extend(new_elements)
                    time.sleep(2)

                except StaleElementReferenceException as se:
                    print(f"Stale element reference: {str(se)}")
                except Exception as e:
                    print(f"An error occurred: {str(e)}")

finally:
    # 브라우저 닫기
    driver.quit()

print("크롤링이 완료되었습니다.")