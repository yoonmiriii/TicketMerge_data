# ticketData
 
## ⚡기획의도⚡
**흩어져있는 콘서트 티켓들의 데이터** 를 가져와<br/><br/>
**하나의 데이터로 만들자** <br/><br/>

## ✌데이터셋 정보✌
해당 데이터는<br/>
[멜론](https://ticket.melon.com/concert/index.htm?genreType=GENRE_CON, '멜론 티켓')<br/>
[인터파크 티켓](https://tickets.interpark.com/contents/genre/concert, '인터파크 티켓')<br/>
[티켓링크](https://www.ticketlink.co.kr/performance/14, '티켓링크')<br/>
[Yes24](http://ticket.yes24.com/New/Genre/GenreMain.aspx?genre=15456, 'yes24 티켓')<br/>
에서 크롤링하여 데이터를 가공하였습니다<br/><br/>

**croll.py와 croll2.py는**<br/>
인터파크 티켓에서의 데이터를 가져오는 파일이고<br/>
croll.py에서는 페이지 하나에서 데이터를 파싱하는 과정을 테스트하였고<br/>
croll2.py에서 HTML태그가 어떻게 저장되어있는지 확인하였으니 직접적으로 데이터를 파싱하는 과정을 거쳤습니다<br/><br/>

**croll3.py와 croll5555.py는**<br/>
마찬가지로 멜론 티켓에서의 데이터를 가져오는 파일이고<br/>
croll3.py에서는 페이지 하나에서 데이터를 파싱하는 과정을 테스트하였고<br/>
croll5555.py에서 HTML태그가 어떻게 저장되어있는지 확인하였으니 직접적으로 데이터를 파싱하는 과정을 거쳤습니다만<br/>
멜론티켓의 경우 링크별로 HTML태그가 뒤죽박죽이었기때문에 예외 방식을 많이 사용하게 되었습니다<br/><br/>

**crolltl.py와 crolltl2.py는**<br/>
마찬가지로 이번에는 티켓링크 에서의 데이터를 가져오는 파일이고<br/>
crolltl.py에서는 페이지 하나에서 데이터를 파싱하는 과정을 테스트하였고<br/>
crolltl2.py에서 HTML태그가 어떻게 저장되어있는지 확인하였으니 직접적으로 데이터를 파싱하는 과정을 거쳤습니다<br/><br/>

**yes24_croll.py는**<br/>
yes24에서의 데이터를 가져오는 파일이고<br/>
바로 데이터를 파싱하는 과정을 거쳤습니다<br/><br/>

## 👍데이터 가공 과정👍
+ 먼저 기획의도에 따라 순서를 정함<br/>
1. **데이터 형식을 통일**할 것<br/>
2. 통일된 데이터를 concat으로 **하나의 파일**로 합칠 것<br/>
3. 컬럼명을 **DB 테이블 컬럼**과 동일하도록 영문으로 변경 할 것<br/>
4. 아티스트 데이터는 **동일 인물이 있다면**으로 중복 제거 할 것<br/>
5. 콘서트 데이터는 **캐스팅 리스트**를 개별 컬럼으로 나눌 것<br/><br/>
    
+ **1. 데이터형식**<br/>
    + **아티스트 이름**의 경우 ['나비'] 같은 형식으로 저장되어 있는 데이터가 있어서 통일시킴<br/>
    + **공연기간**의 경우 시작일만 있는경우, 시작일,종료일이 있는경우가 있어<br/>
    +    두개의 컬럼으로 나눈뒤 종료일 NaN의 경우 fillna()의 ffill 사용하여 시작일과 같게 설정<br/>
+ **2. 하나의 파일**<br/>
    + concat으로 아티스트데이터끼리, 콘서트데이터끼리 합쳐줌<br/>
+ **3. 컬럼명 변경**<br/>
    + 보기 편하라고 지정해둔 한글 컬럼명을 다시 DB에 넣기위해 영문으로 변경<br/>
+ **4. 중복데이터 제거**<br/>
    + Dataframe의 drop_duplicates메소드 이용하여 중복 데이터 제거<br/>
+ **5. 캐스팅리스트 개별화**<br/>
    + **캐스팅리스트**에서 **','으로 스플릿**하여 새로운 컬럼 생성<br/>
    + **가수1,가수2...가수26**으로 컬럼 추가<br/><br/>

+ **6. 추가 사항**<br/>
    + **장르(발라드,댄스 등)** 와 **공연장소(서울/인천/경기, 충청/대전 등)** 의 데이터가 필요하여<br/>
    + numpy라이브러리의 random.randit 사용하여 더미데이터 사용<br/><br/>

## ✔가공 후 이슈✔
데이터 가공 후 테스트 과정에서<br/>
아티스트 데이터에서 중복 데이터 발견<br/>
원인은 중복데이터 제거 당시<br/>
프로필 이미지url은 다르게 저장되어있는데<br/>
이름만 중복을 찾고 지워줄것이라 잘못 판단한거라 추측됨<br/>
DB에서 발견됐기에 DB에서 삭제함<br/><br/>

## 🎈결과🎈
만들어진 데이터파일로 서버와 안드로이드 개발을 진행함<br/>
[서버 깃허브 링크](https://github.com/spiegelgo/aws_ticket_server, '서버 깃허브 링크')<br/>
[안드로이드 깃허브 링크](https://github.com/spiegelgo/TicketMerge-android, '안드로이드 깃허브 링크')<br/>
[프로젝트 기술서 링크](https://docs.google.com/presentation/d/10SK2fhhHQwgktnOjM6e3k2yymyNaWv71hm8S_mkchUI/edit?usp=sharing, '프로젝트 기술서 링크')<br/>
[시연 동영상 링크](https://youtu.be/feCfx006Jew, '시연동영상 링크')<br/>
