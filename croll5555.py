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

# 새 탭에서 링크 클릭 및 작업 수행하는 함수
def click_link_in_new_tab(driver, element):
    try:
        # 현재 탭 핸들 저장
        original_window = driver.current_window_handle
        
        # Actions 클래스를 사용하여 새 탭에서 링크 열기
        action = ActionChains(driver)
        action.key_down(Keys.CONTROL).click(element).key_up(Keys.CONTROL).perform()

        # 모든 탭의 핸들 가져오기
        all_handles = driver.window_handles
        
        # 새로 열린 탭의 핸들 찾기
        new_handle = [handle for handle in all_handles if handle != original_window][0]
        
        # 새로 열린 탭으로 전환
        driver.switch_to.window(new_handle)
        
        # 여기서 새 탭에서 필요한 작업을 수행합니다.
        # 예를 들어, 페이지 소스 가져오기
        wait = WebDriverWait(driver, 3)
        time.sleep(3)
        
        # 페이지 소스 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # 해당 링크 가져오기
        current_url = driver.current_url
        print("URL:", current_url)

        # 상품 제목 가져오기
        title = ''
        title = soup.select_one('p.tit').get_text(strip=True)
        print(f"상품 제목: {title}")

        # 썸네일 URL 가져오기
        thumbnail_URL = ""
        thumbnail_URL = soup.select_one('div.box_consert_thumb img')['src']
        print(f"포스터 URL: {thumbnail_URL}")

        # 상세 포스터 URL 및 작품 설명 이미지 가져오기
        detail_poster_url = ''

        try:            
            # 첫 번째 시도: div.box_img_content img
            if not detail_poster_url:
                detail_poster_element = soup.select_one('div.box_img_content img')
                if detail_poster_element:
                    detail_poster_url = detail_poster_element['src']
                    print(f"상세 포스터 URL: {detail_poster_url}")
                else:
                    print("첫 번째 상세 포스터 URL을 찾을 수 없습니다.")

                # 두 번째 시도: div.box_img_content p img
                if not detail_poster_url:
                    detail_poster_element = soup.select_one('div.box_img_content p img')
                    if detail_poster_element:
                        detail_poster_url = detail_poster_element['src']
                        print(f"상세 포스터 URL: {detail_poster_url}")
                    else:
                        print("두 번째 상세 포스터 URL을 찾을 수 없습니다.")

                    # 세 번째 시도: div.box_img_content a img (상세 포스터 URL이 없을 경우에만)
                    if not detail_poster_url:
                        artwork_images = []
                        artwork_elements = soup.select('div.box_img_content a img')
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
            print(f"An error occurred: {str(e)}")

        # 공연 장소 가져오기
        place = ""
        try:
            place = soup.select_one('dd.txt_info a#performanceHallBtn span.place').get_text(strip=True)
        except AttributeError:
            # 첫 번째 시도 실패 시
            place_element = soup.select_one('dd.txt_info')
            if place_element:
                place = place_element.get_text(strip=True)
        print(f"공연 장소: {place}")

        # 공연 기간 가져오기
        date = ""
        date = soup.select_one('dd#periodInfo').get_text(strip=True)
        print(f"공연 기간: {date}")

        # 캐스팅 리스트 가져오기
        casting_list = []
        artists = soup.select('ul.list_artist li')
        for artist in artists:
            name_tag = artist.select_one('a.txt_name strong.singer')
            if name_tag:  # name_tag가 존재하는 경우에만 실행
                name = name_tag.text.strip()
                if name:  # name이 비어 있지 않은 경우에만 실행
                    try:
                        image_url = artist.select_one('span.thumb img')['src']
                        casting_list.append({'이름': name, '프로필 이미지 URL': image_url})
                    except TypeError:
                        print(f"프로필 이미지 URL을 찾을 수 없습니다. - {name}")
            else:
                print("이름을 찾을 수 없습니다.")

        if not casting_list:
            print("캐스팅 리스트가 없습니다.")

        # CSV 파일에 데이터 추가
        with open('melon_data.csv', mode='a', newline='', encoding='utf-8') as data_file:
            data_writer = csv.writer(data_file)
            cast_names = [casting["이름"] for casting in casting_list]
            data_writer.writerow([title, thumbnail_URL, detail_poster_url, place, date, cast_names, current_url])

        with open('melon_artist.csv', mode='a', newline='', encoding='utf-8') as artist_file:
            artist_writer = csv.writer(artist_file)
            for casting in casting_list:
                artist_writer.writerow([casting["이름"], casting["프로필 이미지 URL"]])
        
        # 새 탭 닫기
        driver.close()
        
        # 원래 탭으로 전환
        driver.switch_to.window(original_window)
        
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
url = 'https://ticket.melon.com/concert/index.htm?genreType=GENRE_CON'

# 웹 페이지 열기
driver.get(url)
driver.maximize_window()
# WebDriverWait를 사용하여 공연 리스트가 로드될 때까지 기다림 (10초로 설정)
wait = WebDriverWait(driver, 5)

try:
    # 페이지를 여러 번 아래로 내리기
    for _ in range(30):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)  # 스크롤 후 대기
    
    # 페이지를 위로 올리기
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.HOME)
    time.sleep(2)  # 스크롤 후 대기
        
    # 초기화
    elements = []

    # 최초의 공연 링크들 가져오기
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#perf_poster > li')))

    # CSV 파일 설정
    with open('melon_data.csv', mode='w', newline='', encoding='utf-8') as data_file, open('melon_artist.csv', mode='w', newline='', encoding='utf-8') as artist_file:
        data_writer = csv.writer(data_file)
        artist_writer = csv.writer(artist_file)

        # CSV 파일 헤더 작성
        data_writer.writerow(["상품 제목", "포스터 URL", "상세 포스터 URL", "공연장소", "공연기간", "캐스팅 리스트", "해당 링크"])
        artist_writer.writerow(["이름", "URL"])

        processed_elements = set()  # 처리된 요소들을 추적하기 위한 집합

        # 공연 리스트 링크 순회
        for element in elements:
            # 이미 처리된 요소는 건너뜀
            if element in processed_elements:
                continue

            try:
                # 요소로 스크롤
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                time.sleep(1)  # 스크롤 후 대기
                

                # 새 탭에서 링크 클릭 및 작업 수행
                click_link_in_new_tab(driver, element)

                # 현재 요소를 처리된 요소로 추가
                processed_elements.add(element)

                time.sleep(2)

            except TimeoutException as te:
                print(f"Timeout occurred: {str(te)}")
            except NoSuchElementException as nse:
                print(f"Element not found: {str(nse)}")
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
