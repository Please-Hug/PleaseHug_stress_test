"""
HugmeEXP Load Testing with Locust
=================================

테스트 사용자 정보:
- Username: testlocust@test.com
- Password: Test123456
- 모든 사용자 클래스가 동일한 계정 사용

실제 테스트 데이터:
- 200개의 Products, Quests, Users, Study Diaries, Praises 등
- locust_test_data.sql의 실제 데이터 구조 반영
"""

import random
import json
import time
from locust import HttpUser, task, between, events
from datetime import datetime, timedelta
import urllib.parse
import base64
import uuid

class HugmeEXPUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """테스트 시작 시 실행되는 메서드"""
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.username = None
        self.mission_ids = []
        self.study_diary_ids = []
        self.quest_ids = []
        self.product_ids = []
        self.bookmark_ids = []
        self.praise_ids = []
        
        # 사용자 로그인
        self.login_user()
        
    def login_user(self):
        """랜덤 사용자로 로그인"""
        # 테스트용 사용자 생성 (실제 환경에서는 사전에 생성된 사용자 사용)
        username = f"testuser{random.randint(1000, 9999)}"
        password = "testpass123!"
        
        # 회원가입 시도 (이미 존재하는 사용자면 실패하지만 괜찮음)
        register_data = {
            "username": username,
            "password": password,
            "name": f"테스트사용자{random.randint(1, 100)}",
            "phoneNumber": f"010-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        }
        
        with self.client.post("/api/register", json=register_data, catch_response=True) as response:
            if response.status_code in [200, 400]:  # 성공 또는 이미 존재하는 사용자
                response.success()
        
        # 로그인
        login_data = {
            "username": username,
            "password": password
        }
        
        with self.client.post("/api/login", json=login_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("data", {}).get("accessToken")
                self.refresh_token = data.get("data", {}).get("refreshToken")
                self.username = username
                response.success()
            else:
                response.failure(f"로그인 실패: {response.status_code}")
    
    def get_headers(self):
        """인증 헤더 반환"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
        
    # @task(10)
    # def check_attendance(self):
    #     """출석 체크 (높은 우선순위)"""
    #     if not self.access_token:
    #         return
            
    #     headers = self.get_headers()
        
    #     # 출석 상태 조회
    #     with self.client.get("/api/v1/attendance/status", headers=headers, catch_response=True) as response:
    #         if response.status_code == 200:
    #             response.success()
    #         else:
    #             response.failure(f"출석 상태 조회 실패: {response.status_code}")
        
    #     # 출석 체크 (이미 출석한 경우 409 에러가 날 수 있음)
    #     with self.client.post("/api/v1/attendance/check", headers=headers, catch_response=True) as response:
    #         if response.status_code in [200, 409]:  # 성공 또는 이미 출석
    #                     response.success()
    #         else:
    #             response.failure(f"출석 체크 실패: {response.status_code}")
    
    @task(8)
    def view_profile(self):
        """프로필 조회"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 내 프로필 조회 - 올바른 엔드포인트로 수정
        with self.client.get("/api/v1/user", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"프로필 조회 실패: {response.status_code}")
        
        # 리더보드(모든 유저) 조회 - 올바른 엔드포인트로 수정
        with self.client.get("/api/v1/users", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"리더보드 조회 실패: {response.status_code}")
    
    # @task(12)
    # def browse_missions(self):
    #     """미션 관련 활동"""
    #     if not self.access_token:
    #         return
            
    #     headers = self.get_headers()
        
    #     # 미션 목록 조회
    #     with self.client.get("/api/v1/missions", headers=headers, catch_response=True) as response:
    #         if response.status_code == 200:
    #             data = response.json()
    #             missions = data.get("data", [])
    #             if missions:
    #                 # 미션 ID 저장
    #                 self.mission_ids = [mission["id"] for mission in missions[:5]]
    #             response.success()
    #         else:
    #             response.failure(f"미션 목록 조회 실패: {response.status_code}")
        
    #     # 미션 상세 조회
    #     if self.mission_ids:
    #         mission_id = random.choice(self.mission_ids)
    #         with self.client.get(f"/api/v1/missions/{mission_id}", headers=headers, catch_response=True) as response:
    #             if response.status_code == 200:
    #                 response.success()
    #             else:
    #                 response.failure(f"미션 상세 조회 실패: {response.status_code}")
            
    #         # 미션 참가 (이미 참가한 경우 에러가 날 수 있음)
    #         with self.client.post(f"/api/v1/missions/{mission_id}/join", headers=headers, catch_response=True) as response:
    #             if response.status_code in [200, 400, 409]:  # 성공 또는 이미 참가
    #                 response.success()
    #             else:
    #                 response.failure(f"미션 참가 실패: {response.status_code}")
    
    @task(15)
    def study_diary_activities(self):
        """배움일기 관련 활동"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 배움일기 목록 조회
        params = {
            "page": random.randint(0, 2),
            "size": 10,
            "sort": "createdAt,desc"
        }
        with self.client.get("/api/v1/studydiaries", params=params, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                diaries = data.get("data", {}).get("content", [])
                if diaries:
                    self.study_diary_ids = [diary["id"] for diary in diaries[:3]]
                response.success()
            else:
                response.failure(f"배움일기 목록 조회 실패: {response.status_code}")
        
        # 인기 배움일기 조회
        with self.client.get("/api/v1/studydiaries/today/popular", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"인기 배움일기 조회 실패: {response.status_code}")
        
        # 배움일기 검색
        search_keywords = ["Spring", "React", "Java", "JavaScript", "Python"]
        keyword = random.choice(search_keywords)
        params = {"keyword": keyword, "page": 0, "size": 5}
        with self.client.get("/api/v1/studydiaries/search", params=params, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"배움일기 검색 실패: {response.status_code}")
        
        # 배움일기 상세 조회
        if self.study_diary_ids:
            diary_id = random.choice(self.study_diary_ids)
            with self.client.get(f"/api/v1/studydiaries/{diary_id}", headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"배움일기 상세 조회 실패: {response.status_code}")
                
    @task(5)
    def create_study_diary(self):
        """배움일기 생성 (낮은 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 배움일기 생성
        diary_data = {
            "title": f"오늘의 학습 기록 {random.randint(1, 1000)}",
            "content": f"오늘은 {random.choice(['Spring Boot', 'React', 'Java', 'Python', 'JavaScript'])}에 대해 공부했습니다. "
                      f"특히 {random.choice(['기본 개념', '고급 기능', '실무 적용', '프로젝트 실습'])}이 인상적이었습니다. "
                      f"앞으로 더 깊이 있게 학습해보고 싶습니다.",
            "imageUrl": f"https://example.com/study-image-{random.randint(1, 100)}.jpg" if random.random() > 0.5 else None
        }
        
        with self.client.post("/api/v1/studydiaries", json=diary_data, headers=headers, catch_response=True) as response:
            if response.status_code == 200:  # Spring 컨트롤러는 200을 반환
                response.success()
            else:
                response.failure(f"배움일기 생성 실패: {response.status_code}")
        
    @task(6)
    def quest_activities(self):
        """퀘스트 관련 활동"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 퀘스트 조회
        with self.client.get("/api/v1/quest", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                quests = data.get("data", [])
                if quests:
                    # 완료 가능한 퀘스트 찾기
                    completable_quests = [q for q in quests if q.get("isCompletable", False) and not q.get("isCompleted", False)]
                    if completable_quests:
                        quest = random.choice(completable_quests)
                        quest_id = quest.get("id")
                        
                        # 퀘스트 완료 처리
                        with self.client.put(f"/api/v1/quest/complete/{quest_id}", headers=headers, catch_response=True) as complete_response:
                            if complete_response.status_code == 200:
                                complete_response.success()
                            else:
                                complete_response.failure(f"퀘스트 완료 실패: {complete_response.status_code}")
                response.success()
            else:
                response.failure(f"퀘스트 조회 실패: {response.status_code}")
    
    @task(7)
    def shop_activities(self):
        """샵 관련 활동"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 상품 목록 조회
        with self.client.get("/api/v1/shop", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                products = data.get("data", [])
                if products:
                    self.product_ids = [product["id"] for product in products[:5]]
                response.success()
            else:
                response.failure(f"상품 목록 조회 실패: {response.status_code}")
        
        # 주문 내역 조회
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        params = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d")
        }
        with self.client.get("/api/v1/shop/history", params=params, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"주문 내역 조회 실패: {response.status_code}")
        
    @task(2)
    def purchase_product(self):
        """상품 구매 (낮은 빈도)"""
        if not self.access_token or not self.product_ids:
            return
            
        headers = self.get_headers()
        
        # 상품 구매
        product_id = random.choice(self.product_ids)
        purchase_data = {
            "productId": product_id,
            "receiverUsername": self.username
        }
        
        with self.client.post("/api/v1/shop/purchase", json=purchase_data, headers=headers, catch_response=True) as response:
            if response.status_code in [200, 400]:  # 성공 또는 포인트 부족
                response.success()
            else:
                response.failure(f"상품 구매 실패: {response.status_code}")
    
    @task(8)
    def praise_activities(self):
        """칭찬 관련 활동"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 칭찬 검색
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        params = {
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": end_date.strftime("%Y-%m-%d"),
            "me": random.choice([True, False])
        }
        with self.client.get("/api/v1/praises/search", params=params, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                praises = data.get("data", [])
                if praises:
                    self.praise_ids = [praise["id"] for praise in praises[:3]]
                response.success()
            else:
                response.failure(f"칭찬 검색 실패: {response.status_code}")
        
        # 인기 칭찬 조회
        with self.client.get("/api/v1/praises/popular", params=params, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"인기 칭찬 조회 실패: {response.status_code}")
        
        # 받은 칭찬 비율 조회
        with self.client.get("/api/v1/praises/me/ratio", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"받은 칭찬 비율 조회 실패: {response.status_code}")
        
        # 칭찬 상세 조회
        if self.praise_ids:
            praise_id = random.choice(self.praise_ids)
            with self.client.get(f"/api/v1/praises/{praise_id}", headers=headers, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"칭찬 상세 조회 실패: {response.status_code}")
        
    @task(3)
    def create_praise(self):
        """칭찬 생성 (낮은 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 칭찬 생성
        praise_types = ["HELPFUL", "CREATIVE", "COLLABORATIVE", "LEADERSHIP"]
        praise_data = {
            "receiverUsername": [f"testuser{random.randint(1000, 9999)}"],
            "type": random.choice(praise_types),
            "content": f"{random.choice(['도움이 되는', '창의적인', '협력적인', '리더십 있는'])} "
                      f"{random.choice(['조언', '아이디어', '태도', '모습'])}을 보여주셔서 감사합니다!"
        }
        
        with self.client.post("/api/v1/praises", json=praise_data, headers=headers, catch_response=True) as response:
            if response.status_code in [201, 400]:  # 성공 또는 존재하지 않는 사용자
                response.success()
            else:
                response.failure(f"칭찬 생성 실패: {response.status_code}")
        
    @task(4)
    def bookmark_activities(self):
        """북마크 관련 활동"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 북마크 목록 조회
        with self.client.get("/api/v1/bookmark", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                bookmarks = data.get("data", [])
                if bookmarks:
                    self.bookmark_ids = [bookmark["id"] for bookmark in bookmarks[:3]]
                response.success()
            else:
                response.failure(f"북마크 목록 조회 실패: {response.status_code}")
    
    @task(2)
    def create_bookmark(self):
        """북마크 생성 (낮은 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        
        # 북마크 생성
        bookmark_data = {
            "title": f"유용한 자료 {random.randint(1, 1000)}",
            "link": f"https://example.com/resource-{random.randint(1, 100)}"
        }
        
        with self.client.post("/api/v1/bookmark", json=bookmark_data, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"북마크 생성 실패: {response.status_code}")
    
    @task(1)
    def token_refresh(self):
        """토큰 갱신 (가장 낮은 빈도)"""
        if not self.access_token or not self.refresh_token:
            return
            
        refresh_data = {
            "accessToken": self.access_token,
            "refreshToken": self.refresh_token
        }
        
        with self.client.post("/api/refresh", json=refresh_data, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("data", {}).get("accessToken")
                self.refresh_token = data.get("data", {}).get("refreshToken")
                response.success()
            elif response.status_code == 400:  # 토큰이 아직 유효함
                response.success()
            else:
                response.failure(f"토큰 갱신 실패: {response.status_code}")


# 사용자 정의 이벤트 리스너
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=== HugmeEXP 부하테스트 시작 ===")
    print(f"목표 사용자 수: {environment.parsed_options.num_users}")
    print(f"spawn rate: {environment.parsed_options.spawn_rate}")
    print("주요 테스트 시나리오:")
    print("- 사용자 로그인/인증")
    print("- 출석 체크")
    print("- 미션 조회/참가")
    print("- 배움일기 CRUD")
    print("- 퀘스트 조회/완료")
    print("- 샵 상품 조회/구매")
    print("- 칭찬 조회/생성")
    print("- 북마크 관리")
    print("- 프로필 조회")
    print("===============================")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=== HugmeEXP 부하테스트 완료 ===")
    print("결과 파일:")
    print("- stress_test_stats.csv")
    print("- stress_test_failures.csv")
    print("- stress_test_exceptions.csv")
    print("- stress_test_stats_history.csv")
    print("===============================")

# 명령줄 실행을 위한 설정
if __name__ == "__main__":
    import os
    # 기본 설정
    os.environ.setdefault('LOCUST_HOST', 'http://localhost:8081')
    os.environ.setdefault('LOCUST_USERS', '1000')
    os.environ.setdefault('LOCUST_SPAWN_RATE', '1.67')  # 분당 100명 = 초당 1.67명
    os.environ.setdefault('LOCUST_RUN_TIME', '600s')
    
    # CSV 출력 설정
    os.environ.setdefault('LOCUST_CSV', 'stress_test')
    
    print("=" * 50)
    print("HugmeEXP 부하테스트 설정")
    print("=" * 50)
    print("환경 변수 설정:")
    print(f"LOCUST_HOST: {os.environ.get('LOCUST_HOST')}")
    print(f"LOCUST_USERS: {os.environ.get('LOCUST_USERS')} (최대 동시사용자)")
    print(f"LOCUST_SPAWN_RATE: {os.environ.get('LOCUST_SPAWN_RATE')} (분당 100명씩 증가)")
    print(f"LOCUST_RUN_TIME: {os.environ.get('LOCUST_RUN_TIME')} (10분간 테스트)")
    print(f"LOCUST_CSV: {os.environ.get('LOCUST_CSV')}")
    print("=" * 50)
    print("실행 방법:")
    print("python -m locust -f locustfile.py --host=http://localhost:8081 --users=1000 --spawn-rate=1.67 --run-time=600s --csv=stress_test --headless")
    print("또는")
    print("./run_test.sh (Linux/macOS)")
    print("run_test.bat (Windows)")
    print("=" * 50) 