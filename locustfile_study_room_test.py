import json
import random
import string
import time
from datetime import datetime, timedelta
from locust import HttpUser, TaskSet, task, between, tag

# 테스트 설정
BASE_URL = ""  # 기본 URL은 비워둠 (locust 실행 시 지정)

# 토큰 설정 - 실제 토큰으로 교체 필요
ADMIN_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE3NTQ0OTgzNjAsInN1YiI6ImFkbWluMjAwNSIsInJvbGUiOiJST0xFX0FETUlOIn0.9VTC1WFxJQ9o2E6VOj6-_MY-qDNdGU_Hl60-xplfdipe0IdvEcL53CziRLhUJsDk6viKF4FUHn-B12tKQ_zRuA"
USER_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE3NTQ0OTgzNDMsInN1YiI6InNqbTFAZ21haWwuY29tIiwicm9sZSI6IlJPTEVfVVNFUiJ9.pV4BYQbQJ0J4IemUtwiW8M5TZrImUNKWVjk0RURWoQwHaHARZ-WFUw7QjhZtXuD2NF94jA1AwkN7HkFWWeCsGw"

# 유틸리티 함수
def generate_random_string(length=10):
    """랜덤 문자열 생성"""
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))

def generate_random_location():
    """랜덤 위치 생성 (서울 지역 내)"""
    # 서울 중심부 좌표 기준
    return {
        "latitude": random.uniform(37.4, 37.7),  # 서울 위도 범위
        "longitude": random.uniform(126.8, 127.2)  # 서울 경도 범위
    }

def generate_random_time():
    """랜덤 시간 생성 (HH:MM 형식)"""
    hour = random.randint(0, 23)
    minute = random.choice([0, 30])  # 30분 단위로 생성
    return f"{hour:02d}:{minute:02d}"

def generate_future_date(days_ahead=1, hours=12, minutes=0):
    """
    미래 날짜 생성 (예약 테스트용)
    days_ahead: 오늘로부터 며칠 후
    hours: 시간 (24시간제)
    minutes: 분
    """
    future_date = datetime.now() + timedelta(days=days_ahead)
    future_date = future_date.replace(hour=hours, minute=minutes, second=0, microsecond=0)
    return future_date.isoformat()

class UserBehavior(TaskSet):
    """사용자 행동 정의 기본 클래스"""
    
    def on_start(self):
        """사용자 세션 시작"""
        # 기본 헤더 설정
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {USER_TOKEN}"
        }
        print(f"User session started with token: {USER_TOKEN[:20]}...")


class AdminUser(HttpUser):
    """관리자 사용자 클래스"""
    wait_time = between(1, 3)  # 작업 간 대기 시간 (초)
    
    def on_start(self):
        """테스트 시작 시 실행"""
        # 기본 헤더 설정 - 고정 토큰 사용
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ADMIN_TOKEN}"
        }
        print(f"Admin session started with token: {ADMIN_TOKEN[:20]}...")
        
        # 테스트에 사용할 데이터 초기화
        self.study_hall_ids = []
        self.study_room_ids = []
        self.reservation_ids = []
    
    # 스터디홀 관련 작업
    @task(3)
    @tag('admin', 'study_hall')
    def create_study_hall(self):
        """스터디홀 생성"""
        # 스터디홀 데이터 생성
        location = generate_random_location()
        open_time = generate_random_time()
        close_time = generate_random_time()
        
        # 오픈 시간이 마감 시간보다 늦으면 교체
        if open_time > close_time:
            open_time, close_time = close_time, open_time
        
        study_hall_data = {
            "name": f"Study Hall {generate_random_string(5)}",
            "description": f"Test study hall created by Locust at {datetime.now().isoformat()}",
            "simpleAddress": f"서울시 {random.choice(['강남구', '서초구', '마포구', '종로구', '중구'])}",
            "address": f"서울시 상세 주소 {random.randint(1, 100)}번지",
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "thumbnail": f"https://example.com/images/study_hall_{random.randint(1, 100)}.jpg",
            "openTime": open_time,
            "closeTime": close_time
        }
        
        with self.client.post(
            "/api/v1/admin/studyhalls",
            json=study_hall_data,
            headers=self.headers,
            catch_response=True,
            name="POST /api/v1/admin/studyhalls"
        ) as response:
            if response.status_code == 201:
                try:
                    study_hall = response.json()
                    study_hall_id = study_hall.get("id")
                    if study_hall_id:
                        self.study_hall_ids.append(study_hall_id)
                        response.success()
                    else:
                        response.failure("생성된 스터디홀 ID가 없습니다")
                except json.JSONDecodeError:
                    response.failure("JSON 응답을 파싱할 수 없습니다")
            else:
                response.failure(f"스터디홀 생성 실패: {response.status_code}")
    
    @task(5)
    @tag('admin', 'study_hall')
    def get_all_study_halls(self):
        """모든 스터디홀 조회"""
        # 페이징 매개변수 설정
        page = random.randint(0, 5)  # 0~5 페이지 중 랜덤
        size = random.choice([10, 20, 50])  # 페이지 크기
        
        with self.client.get(
            f"/api/v1/admin/studyhalls?page={page}&size={size}",
            headers=self.headers,
            catch_response=True,
            name="GET /api/v1/admin/studyhalls"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"스터디홀 목록 조회 실패: {response.status_code}")
    
    @task(2)
    @tag('admin', 'study_hall')
    def get_study_hall_by_id(self):
        """특정 스터디홀 조회"""
        if not self.study_hall_ids:
            return
        
        study_hall_id = random.choice(self.study_hall_ids)
        
        with self.client.get(
            f"/api/v1/admin/studyhalls/{study_hall_id}",
            headers=self.headers,
            catch_response=True,
            name="GET /api/v1/admin/studyhalls/{id}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"스터디홀 조회 실패: {response.status_code}")
                # ID가 유효하지 않은 경우 목록에서 제거
                if response.status_code == 404 and study_hall_id in self.study_hall_ids:
                    self.study_hall_ids.remove(study_hall_id)
    
    @task(1)
    @tag('admin', 'study_hall')
    def update_study_hall(self):
        """스터디홀 정보 수정"""
        if not self.study_hall_ids:
            return
        
        study_hall_id = random.choice(self.study_hall_ids)
        location = generate_random_location()
        
        update_data = {
            "name": f"Updated Study Hall {generate_random_string(5)}",
            "description": f"Updated description at {datetime.now().isoformat()}",
            "simpleAddress": f"서울시 {random.choice(['강남구', '서초구', '마포구', '종로구', '중구'])}",
            "address": f"서울시 상세 주소 {random.randint(1, 100)}번지",
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "thumbnail": f"https://example.com/images/updated_hall_{random.randint(1, 100)}.jpg",
            "openTime": f"{random.randint(8, 10):02d}:00",
            "closeTime": f"{random.randint(18, 22):02d}:00"
        }
        
        with self.client.put(
            f"/api/v1/admin/studyhalls/{study_hall_id}",
            json=update_data,
            headers=self.headers,
            catch_response=True,
            name="PUT /api/v1/admin/studyhalls/{id}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"스터디홀 수정 실패: {response.status_code}")
                # ID가 유효하지 않은 경우 목록에서 제거
                if response.status_code == 404 and study_hall_id in self.study_hall_ids:
                    self.study_hall_ids.remove(study_hall_id)
    
    @task(1)
    @tag('admin', 'study_hall')
    def delete_study_hall(self):
        """스터디홀 삭제"""
        if not self.study_hall_ids:
            return
        
        study_hall_id = random.choice(self.study_hall_ids)
        
        with self.client.delete(
            f"/api/v1/admin/studyhalls/{study_hall_id}",
            headers=self.headers,
            catch_response=True,
            name="DELETE /api/v1/admin/studyhalls/{id}"
        ) as response:
            if response.status_code == 204:
                # 성공적으로 삭제된 경우 목록에서 제거
                if study_hall_id in self.study_hall_ids:
                    self.study_hall_ids.remove(study_hall_id)
                response.success()
            else:
                response.failure(f"스터디홀 삭제 실패: {response.status_code}")
    
    # 스터디룸 관련 작업
    @task(3)
    @tag('admin', 'study_room')
    def create_study_room(self):
        """스터디룸 생성"""
        if not self.study_hall_ids:
            return
        
        study_hall_id = random.choice(self.study_hall_ids)
        
        room_data = {
            "name": f"Room {generate_random_string(5)}",
            "maxNum": random.randint(2, 10),
            "thumbnail": f"https://example.com/images/room_{random.randint(1, 100)}.jpg"
        }
        
        with self.client.post(
            f"/api/v1/admin/studyhalls/{study_hall_id}/rooms",
            json=room_data,
            headers=self.headers,
            catch_response=True,
            name="POST /api/v1/admin/studyhalls/{id}/rooms"
        ) as response:
            if response.status_code == 201:
                try:
                    room = response.json()
                    room_id = room.get("id")
                    if room_id:
                        self.study_room_ids.append((study_hall_id, room_id))
                        response.success()
                    else:
                        response.failure("생성된 스터디룸 ID가 없습니다")
                except json.JSONDecodeError:
                    response.failure("JSON 응답을 파싱할 수 없습니다")
            else:
                response.failure(f"스터디룸 생성 실패: {response.status_code}")
                # 스터디홀 ID가 유효하지 않은 경우 목록에서 제거
                if response.status_code == 404 and study_hall_id in self.study_hall_ids:
                    self.study_hall_ids.remove(study_hall_id)
    
    @task(2)
    @tag('admin', 'study_room')
    def get_all_rooms_in_hall(self):
        """특정 스터디홀의 모든 스터디룸 조회"""
        if not self.study_hall_ids:
            return
        
        study_hall_id = random.choice(self.study_hall_ids)
        
        with self.client.get(
            f"/api/v1/admin/studyhalls/{study_hall_id}/rooms",
            headers=self.headers,
            catch_response=True,
            name="GET /api/v1/admin/studyhalls/{id}/rooms"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"스터디룸 목록 조회 실패: {response.status_code}")
                # 스터디홀 ID가 유효하지 않은 경우 목록에서 제거
                if response.status_code == 404 and study_hall_id in self.study_hall_ids:
                    self.study_hall_ids.remove(study_hall_id)
    
    @task(1)
    @tag('admin', 'study_room')
    def update_study_room(self):
        """스터디룸 정보 수정"""
        if not self.study_room_ids:
            return
        
        study_hall_id, room_id = random.choice(self.study_room_ids)
        
        update_data = {
            "name": f"Updated Room {generate_random_string(5)}",
            "maxNum": random.randint(2, 15),
            "thumbnail": f"https://example.com/images/updated_room_{random.randint(1, 100)}.jpg"
        }
        
        with self.client.put(
            f"/api/v1/admin/studyhalls/{study_hall_id}/rooms/{room_id}",
            json=update_data,
            headers=self.headers,
            catch_response=True,
            name="PUT /api/v1/admin/studyhalls/{id}/rooms/{roomId}"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"스터디룸 수정 실패: {response.status_code}")
                # ID가 유효하지 않은 경우 목록에서 제거
                if response.status_code == 404:
                    if (study_hall_id, room_id) in self.study_room_ids:
                        self.study_room_ids.remove((study_hall_id, room_id))
    
    @task(1)
    @tag('admin', 'study_room')
    def delete_study_room(self):
        """스터디룸 삭제"""
        if not self.study_room_ids:
            return
        
        study_hall_id, room_id = random.choice(self.study_room_ids)
        
        with self.client.delete(
            f"/api/v1/admin/studyhalls/{study_hall_id}/rooms/{room_id}",
            headers=self.headers,
            catch_response=True,
            name="DELETE /api/v1/admin/studyhalls/{id}/rooms/{roomId}"
        ) as response:
            if response.status_code == 204:
                # 성공적으로 삭제된 경우 목록에서 제거
                if (study_hall_id, room_id) in self.study_room_ids:
                    self.study_room_ids.remove((study_hall_id, room_id))
                response.success()
            else:
                response.failure(f"스터디룸 삭제 실패: {response.status_code}")
    
    # 예약 관리 작업
    @task(2)
    @tag('admin', 'reservation')
    def get_all_reservations(self):
        """모든 예약 조회"""
        # 페이징 매개변수 설정
        page = random.randint(0, 5)  # 0~5 페이지 중 랜덤
        size = random.choice([10, 20, 50])  # 페이지 크기
        
        with self.client.get(
            f"/api/v1/admin/reservations?page={page}&size={size}",
            headers=self.headers,
            catch_response=True,
            name="GET /api/v1/admin/reservations"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # 응답에서 예약 ID 추출하여 저장
                    if "data" in data and "content" in data["data"]:
                        for reservation in data["data"]["content"]:
                            if "id" in reservation and reservation["id"] not in self.reservation_ids:
                                self.reservation_ids.append(reservation["id"])
                    response.success()
                except json.JSONDecodeError:
                    response.failure("JSON 응답을 파싱할 수 없습니다")
            else:
                response.failure(f"예약 목록 조회 실패: {response.status_code}")
    
    @task(1)
    @tag('admin', 'reservation')
    def cancel_reservation(self):
        """예약 강제 취소"""
        if not self.reservation_ids:
            return
        
        reservation_id = random.choice(self.reservation_ids)
        
        with self.client.delete(
            f"/api/v1/admin/reservations/{reservation_id}",
            headers=self.headers,
            catch_response=True,
            name="DELETE /api/v1/admin/reservations/{id}"
        ) as response:
            if response.status_code == 200:
                # 성공적으로 취소된 경우 목록에서 제거
                if reservation_id in self.reservation_ids:
                    self.reservation_ids.remove(reservation_id)
                response.success()
            else:
                response.failure(f"예약 취소 실패: {response.status_code}")
                # ID가 유효하지 않은 경우 목록에서 제거
                if response.status_code == 404 and reservation_id in self.reservation_ids:
                    self.reservation_ids.remove(reservation_id)


class RegularUser(HttpUser):
    """일반 사용자 클래스"""
    wait_time = between(1, 5)  # 작업 간 대기 시간 (초)
    
    # 사용자 계정 풀에서 랜덤하게 선택
    user_index = 0
    
    def on_start(self):
        """테스트 시작 시 실행"""
        # 사용자 계정 선택 (라운드 로빈 방식)
        RegularUser.user_index = (RegularUser.user_index + 1) % USER_COUNT
        self.email = USER_EMAILS[RegularUser.user_index]
        self.password = USER_PASSWORDS[RegularUser.user_index]
        
        # 기본 헤더 설정
        self.headers = {"Content-Type": "application/json"}
        
        # 사용자 계정 등록 및 로그인
        self.register_and_login()
        
        # 테스트에 사용할 데이터 초기화
        self.study_hall_ids = []
        self.study_room_ids = []
        self.my_reservations = []
    
    def register_and_login(self):
        """사용자 계정 등록 및 로그인"""
        # 사용자 계정 등록 시도
        register_data = {
            "email": self.email,
            "password": self.password,
            "name": f"User {self.email.split('@')[0]}"
        }
        
        with self.client.post(
            "/api/v1/auth/register",
            json=register_data,
            headers=self.headers,
            catch_response=True,
            name="POST /api/v1/auth/register (User)"
        ) as response:
            # 201: 성공, 400: 이미 존재하는 계정
            if response.status_code not in [201, 400]:
                response.failure(f"사용자 계정 등록 실패: {response.status_code}")
                return
        
        # 로그인 시도
        login_data = {
            "email": self.email,
            "password": self.password
        }
        
        with self.client.post(
            "/api/v1/auth/login",
            json=login_data,
            headers=self.headers,
            catch_response=True,
            name="POST /api/v1/auth/login (User)"
        ) as response:
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    self.auth_token = response_data.get("token")
                    if self.auth_token:
                        self.headers["Authorization"] = f"Bearer {self.auth_token}"
                        response.success()
                    else:
                        response.failure("토큰이 응답에 없습니다")
                except json.JSONDecodeError:
                    response.failure("JSON 응답을 파싱할 수 없습니다")
            else:
                response.failure(f"사용자 로그인 실패: {response.status_code}")
    
    # 스터디홀 검색 및 조회 작업
    @task(5)
    @tag('user', 'search')
    def search_study_halls(self):
        """스터디홀 검색"""
        # 검색 매개변수 설정
        page = random.randint(0, 3)  # 0~3 페이지 중 랜덤
        size = random.choice([10, 20, 30])  # 페이지 크기
        
        # 랜덤 검색 조건 생성
        search_params = {}
        
        # 30% 확률로 이름 검색 추가
        if random.random() < 0.3:
            search_params["name"] = random.choice(["Study", "Hall", "Room", "Place", "Space"])
        
        # 30% 확률로 주소 검색 추가
        if random.random() < 0.3:
            search_params["address"] = random.choice(['강남', '서초', '마포', '종로', '중구'])
        
        # 지도 범위 검색 (20% 확률)
        if random.random() < 0.2:
            location = generate_random_location()
            search_params["latitude"] = location["latitude"]
            search_params["longitude"] = location["longitude"]
            search_params["distance"] = random.choice([1, 3, 5, 10])  # km 단위
        
        # 질의어 생성
        query_string = "&".join([f"{key}={value}" for key, value in search_params.items()])
        query_string = f"page={page}&size={size}&{query_string}" if query_string else f"page={page}&size={size}"
        
        with self.client.get(
            f"/api/v1/studyroom/map?{query_string}",
            headers=self.headers,
            catch_response=True,
            name="GET /api/v1/studyroom/map"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # 응답에서 스터디홀 ID 추출하여 저장
                    if "data" in data and "content" in data["data"]:
                        for hall in data["data"]["content"]:
                            if "id" in hall and hall["id"] not in self.study_hall_ids:
                                self.study_hall_ids.append(hall["id"])
                    response.success()
                except json.JSONDecodeError:
                    response.failure("JSON 응답을 파싱할 수 없습니다")
            else:
                response.failure(f"스터디홀 검색 실패: {response.status_code}")
    
    @task(3)
    @tag('user', 'study_hall')
    def get_study_hall_detail(self):
        """스터디홀 상세 정보 조회"""
        if not self.study_hall_ids:
            # 스터디홀 ID가 없는 경우 검색부터 실행
            self.search_study_halls()
            if not self.study_hall_ids:
                return
        
        study_hall_id = random.choice(self.study_hall_ids)
        
        with self.client.get(
            f"/api/v1/studyroom/halls/{study_hall_id}",
            headers=self.headers,
            catch_response=True,
            name="GET /api/v1/studyroom/halls/{id}"
        ) as response:
            if response.status_code == 200:
                try:
                    hall_data = response.json()
                    # 스터디룸 정보 추출
                    if "rooms" in hall_data:
                        for room in hall_data["rooms"]:
                            if "id" in room:
                                room_id = room["id"]
                                if (study_hall_id, room_id) not in self.study_room_ids:
                                    self.study_room_ids.append((study_hall_id, room_id))
                    response.success()
                except json.JSONDecodeError:
                    response.failure("JSON 응답을 파싱할 수 없습니다")
            else:
                response.failure(f"스터디홀 상세 조회 실패: {response.status_code}")
                # ID가 유효하지 않은 경우 목록에서 제거
                if response.status_code == 404 and study_hall_id in self.study_hall_ids:
                    self.study_hall_ids.remove(study_hall_id)
    
    # 예약 관련 작업
    @task(2)
    @tag('user', 'reservation')
    def create_reservation(self):
        """스터디룸 예약 생성"""
        if not self.study_room_ids:
            # 스터디룸 ID가 없는 경우 스터디홀 상세 조회부터 실행
            self.get_study_hall_detail()
            if not self.study_room_ids:
                return
        
        study_hall_id, room_id = random.choice(self.study_room_ids)
        
        # 예약 시간 생성 (현재로부터 1~7일 이내의 미래 시간)
        start_datetime = generate_future_datetime(days_ahead=random.randint(1, 7))
        # 예약 시간은 1~3시간 사이
        end_datetime = start_datetime + timedelta(hours=random.randint(1, 3))
        
        reservation_data = {
            "studyHallId": study_hall_id,
            "roomId": room_id,
            "startDateTime": start_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "endDateTime": end_datetime.strftime("%Y-%m-%dT%H:%M:%S"),
            "numOfUsers": random.randint(1, 4)
        }
        
        with self.client.post(
            "/api/v1/studyroom/reservations",
            json=reservation_data,
            headers=self.headers,
            catch_response=True,
            name="POST /api/v1/studyroom/reservations"
        ) as response:
            if response.status_code == 201:
                try:
                    reservation = response.json()
                    reservation_id = reservation.get("id")
                    if reservation_id:
                        self.my_reservations.append(reservation_id)
                        response.success()
                    else:
                        response.failure("생성된 예약 ID가 없습니다")
                except json.JSONDecodeError:
                    response.failure("JSON 응답을 파싱할 수 없습니다")
            else:
                response.failure(f"예약 생성 실패: {response.status_code}")
    
    @task(3)
    @tag('user', 'reservation')
    def get_my_reservations(self):
        """내 예약 목록 조회"""
        # 페이징 매개변수 설정
        page = random.randint(0, 2)  # 0~2 페이지 중 랜덤
        size = random.choice([5, 10, 20])  # 페이지 크기
        
        with self.client.get(
            f"/api/v1/studyroom/reservations/me?page={page}&size={size}",
            headers=self.headers,
            catch_response=True,
            name="GET /api/v1/studyroom/reservations/me"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # 응답에서 예약 ID 추출하여 저장
                    if "data" in data and "content" in data["data"]:
                        self.my_reservations = []
                        for reservation in data["data"]["content"]:
                            if "id" in reservation:
                                self.my_reservations.append(reservation["id"])
                    response.success()
                except json.JSONDecodeError:
                    response.failure("JSON 응답을 파싱할 수 없습니다")
            else:
                response.failure(f"예약 목록 조회 실패: {response.status_code}")
    
    @task(1)
    @tag('user', 'reservation')
    def cancel_my_reservation(self):
        """내 예약 취소"""
        if not self.my_reservations:
            # 예약 ID가 없는 경우 예약 목록 조회부터 실행
            self.get_my_reservations()
            if not self.my_reservations:
                return
        
        reservation_id = random.choice(self.my_reservations)
        
        with self.client.delete(
            f"/api/v1/studyroom/reservations/{reservation_id}",
            headers=self.headers,
            catch_response=True,
            name="DELETE /api/v1/studyroom/reservations/{id}"
        ) as response:
            if response.status_code == 200:
                # 성공적으로 취소된 경우 목록에서 제거
                if reservation_id in self.my_reservations:
                    self.my_reservations.remove(reservation_id)
                response.success()
            else:
                response.failure(f"예약 취소 실패: {response.status_code}")
                # ID가 유효하지 않은 경우 목록에서 제거
                if response.status_code == 404 and reservation_id in self.my_reservations:
                    self.my_reservations.remove(reservation_id)


# Locust 실행 설정
class StudyRoomLoadTest(HttpUser):
    """
    메인 Locust 테스트 클래스
    이 클래스는 실제로 테스트를 실행하지 않고, 다른 사용자 클래스를 선택하는 역할만 합니다.
    """
    abstract = True  # 이 클래스는 직접 인스턴스화되지 않음
    
    # 테스트 실행 시 AdminUser와 RegularUser 클래스를 사용하도록 설정
    tasks = {}


# 테스트 실행 시 사용할 사용자 클래스 설정
AdminUser.host = ""  # 실제 API 서버 주소로 설정 필요
RegularUser.host = ""  # 실제 API 서버 주소로 설정 필요

# 테스트 실행 방법:
# locust -f locustfile_study_room_test.py AdminUser RegularUser --host=http://your-api-server