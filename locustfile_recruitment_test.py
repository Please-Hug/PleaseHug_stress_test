from locust import HttpUser, task, between
import json
import random
from datetime import datetime


class RecruitmentApiUser(HttpUser):
    wait_time = between(1, 3)  # 요청 간 1-3초 대기

    # 테스트용 데이터
    keywords = ["개발자", "프론트엔드", "백엔드", "데이터", "AI", "머신러닝", "디자인", "PM", "QA"]
    tech_stacks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 기술스택 ID
    locations = ["서울", "경기", "부산", "대구", "인천"]
    experience_levels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # 경력 범위 0-10년
    education_levels = [0, 10, 20, 30, 40, 50]  # 교육 수준 ID
    tag_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # 태그 ID들

    def on_start(self):
        """테스트 시작 시 실행"""
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE3NTQ2MjQyNjEsInN1YiI6InRlc3QwMSIsInJvbGUiOiJST0xFX1VTRVIifQ.8qZrKDa-zALjGxpJSXdMAW8C6_smXoNDTSB-fS-l4yOpnk5DeMfkS5Cfy0ZgoQmIOH0TQnLHNBTEMLEOG-QBew"
        }
        self.scraping_headers = {
            "Content-Type": "application/json",
            "X-API-Key": "65f91852-3379-47a3-bcdb-b85241fc6b33"
        }

    @task(30)  # 가장 높은 비중 - 메인 목록 조회
    def list_recruitments(self):
        """채용 공고 목록 조회 - 다양한 필터 조건으로 테스트"""
        # 경력 범위 설정 (experienceMin, experienceMax)
        exp_min = random.choice(self.experience_levels) if random.random() > 0.8 else None
        exp_max = None
        if exp_min is not None and random.random() > 0.5:
            exp_max = random.choice([x for x in self.experience_levels if x >= exp_min])

        # 연봉 범위 설정
        salary_min = random.choice([0, 3000, 4000, 5000, 6000]) if random.random() > 0.7 else None
        salary_max = None
        if salary_min is not None and random.random() > 0.5:
            salary_max = random.choice([x for x in [3000, 5000, 6000, 7000, 8000, 10000] if x >= salary_min])

        # 기술스택 리스트 (1-3개 선택)
        tech_stack_list = random.sample(self.tech_stacks, random.randint(1, 3)) if random.random() > 0.6 else None

        # 태그 리스트 (1-2개 선택)
        tag_list = random.sample(self.tag_ids, random.randint(1, 2)) if random.random() > 0.8 else None

        # 위치 좌표 (서울 지역 기준 예시)
        use_location_coords = random.random() > 0.9

        params = {
            "page": random.randint(0, 10),
            "salaryMin": salary_min,
            "salaryMax": salary_max,
            "experienceMin": exp_min,
            "experienceMax": exp_max,
            "education": random.choice(self.education_levels) if random.random() > 0.9 else None,
            "workLocation": random.choice(self.locations) if random.random() > 0.6 else None,
        }

        # 리스트 파라미터 처리
        if tech_stack_list:
            params["techStacks"] = tech_stack_list
            params["techStackCount"] = len(tech_stack_list)

        if tag_list:
            params["tags"] = tag_list
            params["tagCount"] = len(tag_list)

        # 좌표 기반 검색 (가끔씩만)
        if use_location_coords:
            params.update({
                "topLeftLat": 37.7,      # 북쪽 위도
                "topLeftLng": 126.7,     # 서쪽 경도
                "bottomRightLat": 37.4,  # 남쪽 위도
                "bottomRightLng": 127.2  # 동쪽 경도
            })

        # None 값 제거
        params = {k: v for k, v in params.items() if v is not None}

        with self.client.get(
            "/api/v1/recruitments",
            params=params,
            headers=self.headers,
            name="GET /api/v1/recruitments",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # 응답 데이터 검증
                    if 'data' in data and isinstance(data['data'], list):
                        response.success()  # 성공
                except json.JSONDecodeError:
                    response.failure("응답이 유효한 JSON이 아닙니다")
            else:
                response.failure(f"예상하지 못한 상태 코드: {response.status_code}")

    @task(20)  # 두 번째로 높은 비중 - 검색 기능
    def search_companies(self):
        """회사명/공고 제목 키워드 검색"""
        keyword = random.choice(self.keywords)

        with self.client.get(
            "/api/v1/recruitments/companies",
            params={"keyword": keyword},
            headers=self.headers,
            name="GET /api/v1/recruitments/companies",
            catch_response=True
        ) as response:
            if response.status_code in [200, 204]:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if 'data' in data:
                            response.success()  # 성공
                    except json.JSONDecodeError:
                        response.failure("응답이 유효한 JSON이 아닙니다")
                else:
                    response.success()  # 204도 성공
            else:
                response.failure(f"예상하지 못한 상태 코드: {response.status_code}")

    @task(15)  # 홈 화면용 최신 공고 조회
    def find_latest_recruitments(self):
        """최신 채용 공고 조회 (홈 화면용)"""
        with self.client.get(
            "/api/v1/recruitments/home",
            headers=self.headers,
            name="GET /api/v1/recruitments/home",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and isinstance(data['data'], list):
                        # 최대 5개까지 반환되는지 확인
                        if len(data['data']) <= 5:
                            response.success()  # 성공
                        else:
                            response.failure("응답 데이터가 5개를 초과합니다")
                    else:
                        response.failure("응답 데이터 구조가 올바르지 않습니다")
                except json.JSONDecodeError:
                    response.failure("응답이 유효한 JSON이 아닙니다")
            else:
                response.failure(f"예상하지 못한 상태 코드: {response.status_code}")

    @task(10)  # 상세 조회
    def find_recruitment_detail(self):
        """채용 공고 상세 조회"""
        # 실제 존재하는 ID 범위를 가정 (1-1000)
        recruitment_id = random.randint(1, 1000)

        with self.client.get(
            f"/api/v1/recruitments/{recruitment_id}",
            headers=self.headers,
            name="GET /api/v1/recruitments/{id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data:
                        response.success()  # 성공
                    else:
                        response.failure("응답 데이터가 없습니다")
                except json.JSONDecodeError:
                    response.failure("응답이 유효한 JSON이 아닙니다")
            elif response.status_code == 404:
                response.success()  # 존재하지 않는 ID는 정상적인 응답
            else:
                response.failure(f"예상하지 못한 상태 코드: {response.status_code}")

    @task(8)  # 필터 옵션 조회
    def get_filters(self):
        """채용 공고 필터 옵션 조회"""
        with self.client.get(
            "/api/v1/recruitments/filters",
            headers=self.headers,
            name="GET /api/v1/recruitments/filters",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data:
                        response.success()  # 성공
                    else:
                        response.failure("응답 데이터가 없습니다")
                except json.JSONDecodeError:
                    response.failure("응답이 유효한 JSON이 아닙니다")
            else:
                response.failure(f"예상하지 못한 상태 코드: {response.status_code}")

    @task(5)  # 스크래핑 API (상대적으로 낮은 빈도)
    def create_recruitment_scraping(self):
        """채용 공고 스크래핑 API"""
        # 실제 성공 케이스와 동일한 구조로 테스트 데이터 생성
        test_data = {
            "recruitmentSourceId": f"wanted::{random.randint(100000, 999999)}",
            "title": f"백엔드 엔지니어 {random.randint(1, 100)}",
            "education": random.choice([0, 10, 20]),
            "experienceMin": random.choice([0, 1, 3]),
            "experienceMax": random.choice([5, 7, 10]),
            "qualification": "【 이런 분을 찾고 있어요 】\n• 알고리즘과 자료구조에 대한 이해를 갖추신 분\n• 빠르게 학습하는 역량을 갖추신 분\n• 코드잇의 비전에 공감하며, 원활한 커뮤니케이션 능력을 갖추신 분",
            "advantage": "【 이런 분이면 더 좋아요 】\n• 컴퓨터 과학과 또는 컴퓨터 공학과 출신이신 분\n• 코드잇의 개발 스택(주요 업무에 기술됨)에 대한 전문성이 있으신 분\n• 영어를 잘 하시는 분 (Bilingual일 경우 추가 우대)\n• IT 스타트업에서 근무해보신 분",
            "welfare": "1. 최고의 팀원에게 최고의 보상을 제공해요.\n• 최고의 동료들이 모인 팀\n• 최고 수준의 보상 지향\n\n2. 몰입을 위한 최적의 환경을 지원해요.\n• 주 40시간 유연근무제 (코어타임 오후 1~5시)\n• 자유로운 재택근무 (월금 비코어타임 및 화수목 재택근무 가능)\n• 직군별 최고 사양의 맥북과 모니터 제공, 장비지원금 별도 지원\n• 도서, 교육 등 자기계발을 위한 비용 지원\n• 동료 및 리더와의 상시 피드백 문화\n\n3. 건강과 행복을 위한 복지를 제공해요.\n• 점심, 저녁 식대 지원 (각 최대 12,000원)\n• 무제한 간식 제공, 매년 명절 및 생일 축하 선물\n• 연 100만원 상당의 종합 건강검진 지원\n• 50만원 상당의 경조사비 지원\n• 주차비 지원 \n\n4. 친밀한 문화를 함께 만들어가요.\n• 신뢰를 바탕으로 한 반말 문화\n• 랜덤점심, TGIM, 비어토크\n• 사내 동아리 활동 지원",
            "workLocation": "중구 청계천로 100 시그니쳐타워 동관 10층",
            "latitude": "37.5674783",
            "longitude": "126.9884121",
            "salaryMin": random.choice([0, 3000, 4000]),
            "salaryMax": random.choice([0, 6000, 7000, 8000]),
            "link": f"https://www.wanted.co.kr/wd/{random.randint(100000, 999999)}",
            "source": "WANTED",
            "dueDate": "9999-12-31T23:59:59",
            "company": {
                "companyName": f"테스트회사{random.randint(1, 50)}",
                "companyAddress": "중구 청계천로 100 시그니쳐타워 동관 10층",
                "latitude": "37.56747830",
                "longitude": "126.98841210",
                "establishmentDate": "2017-01-01",
                "companyImageUrl": f"https://static.wanted.co.kr/images/wdes/0_{random.randint(1, 10)}.png",
                "companyDescription": "",
                "companySourceId": f"wanted::{random.randint(1000, 9999)}"
            },
            "requiredSkills": [],
            "tags": [
                {"tagName": "51~300명"},
                {"tagName": "AI 선도 기업"},
                {"tagName": "건강검진지원"},
                {"tagName": "설립4~9년"},
                {"tagName": "식대지원"},
                {"tagName": "연봉 업계평균이상"},
                {"tagName": "원티드 픽"},
                {"tagName": "유망산업"},
                {"tagName": "인원 급성장"},
                {"tagName": "자기계발지원"},
                {"tagName": "장비지원"},
                {"tagName": "커피·스낵바"}
            ]
        }

        # 더 간단한 에러 처리로 변경
        response = self.client.post(
            "/api/v1/recruitments/scrape",
            json=test_data,
            headers=self.scraping_headers,
            name="POST /api/v1/recruitments/scrape"
        )

        # 상세한 에러 로깅
        if response.status_code != 201:
            try:
                error_detail = response.json()
                print(f"스크래핑 실패: {response.status_code} - {error_detail}")
            except:
                print(f"스크래핑 실패: {response.status_code} - 응답 내용 파싱 실패")

    @task(2)  # 대용량 페이지 요청 테스트
    def test_large_page_request(self):
        """큰 페이지 번호로 요청하여 성능 테스트"""
        large_page = random.randint(100, 1000)

        with self.client.get(
            "/api/v1/recruitments",
            params={"page": large_page},
            headers=self.headers,
            name="GET /api/v1/recruitments (Large Page)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data:
                        response.success()  # 성공 (빈 결과일 수도 있음)
                    else:
                        response.failure("응답 데이터가 없습니다")
                except json.JSONDecodeError:
                    response.failure("응답이 유효한 JSON이 아닙니다")
            else:
                response.failure(f"예상하지 못한 상태 코드: {response.status_code}")


class RecruitmentApiLoadTest(HttpUser):
    """고부하 테스트용 별도 클래스"""
    wait_time = between(0.1, 0.5)  # 더 짧은 대기시간으로 부하 증가

    def on_start(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer abcdefg"
        }

    @task(1)
    def rapid_fire_requests(self):
        """연속적인 빠른 요청으로 부하 테스트"""
        endpoints = [
            "/api/v1/recruitments",
            "/api/v1/recruitments/home",
            "/api/v1/recruitments/filters"
        ]

        endpoint = random.choice(endpoints)
        with self.client.get(endpoint, headers=self.headers, name=f"Rapid {endpoint}"):
            pass


# 사용 예시:
# 일반 테스트: locust -f locustfile_recruitment_test.py RecruitmentApiUser --host=http://localhost:8080
# 고부하 테스트: locust -f locustfile_recruitment_test.py RecruitmentApiLoadTest --host=http://localhost:8080
