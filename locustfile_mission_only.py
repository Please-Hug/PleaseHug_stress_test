"""
HugmeEXP 미션 전용 부하테스트
=============================

미션 관련 기능만을 집중적으로 테스트하는 전용 스크립트

테스트 시나리오:
- 미션 상세 조회
- 미션 참가 (챌린지)
- 미션 태스크 조회 및 완료
- 미션 진행상황 확인
"""

import random
import json
import time
from locust import HttpUser, task, between, events
from datetime import datetime, timedelta
import urllib.parse
import base64
import uuid

class MissionFocusedUser(HttpUser):
    wait_time = between(1, 3)
    connection_timeout = 60.0  # 연결 타임아웃 60초
    network_timeout = 60.0     # 네트워크 타임아웃 60초
    
    def on_start(self):
        """테스트 시작 시 실행되는 메서드"""
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        self.username = None
        self.mission_ids = list(range(1, 21))  # 1~20번 미션 ID
        
        # 사용자 로그인
        self.login_user()
        
    def login_user(self):
        """랜덤 사용자로 로그인"""
        # 테스트용 사용자 생성
        username = f"mission_test_{random.randint(1000, 9999)}"
        password = "testpass123!"
        
        # 회원가입 시도
        register_data = {
            "username": username,
            "password": password,
            "name": f"미션테스터{random.randint(1, 100)}",
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
                response.failure(f"미션 테스터 로그인 실패: {response.status_code}")
    
    def get_headers(self):
        """인증 헤더 반환"""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
        
    @task(20)
    def explore_missions(self):
        """미션 탐색 및 상세 조회 (높은 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        mission_id = random.choice(self.mission_ids)
        
        # 미션 상세 조회
        with self.client.get(f"/api/v1/missions/{mission_id}", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                mission_info = data.get("data", {})
                
                # 미션 정보 로깅 (선택사항)
                mission_name = mission_info.get("name", f"미션 {mission_id}")
                
                response.success()
            elif response.status_code == 404:
                # 존재하지 않는 미션 ID인 경우 성공으로 처리
                response.success() 
            else:
                response.failure(f"미션 {mission_id} 상세 조회 실패: {response.status_code}")

    @task(15)
    def join_mission_challenge(self):
        """미션 참가 및 챌린지 관리 (높은 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        mission_id = random.choice(self.mission_ids)
        
        # 미션 챌린지 조회 (참가 현황 확인)
        with self.client.get(f"/api/v1/missions/{mission_id}/challenges", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                challenge_data = data.get("data", {})
                
                # 이미 참가한 미션인지 확인
                is_joined = challenge_data.get("isJoined", False)
                
                response.success()
            elif response.status_code == 404:
                # 아직 참가하지 않은 미션
                response.success()
            else:
                response.failure(f"미션 {mission_id} 챌린지 조회 실패: {response.status_code}")
        
        # 미션 참가 시도
        with self.client.post(f"/api/v1/missions/{mission_id}/challenges", headers=headers, catch_response=True) as response:
            if response.status_code == 201:
                # 새로 참가 성공
                response.success()
            elif response.status_code in [400, 409]:
                # 이미 참가했거나 참가 불가능한 미션
                response.success()
            elif response.status_code == 404:
                # 존재하지 않는 미션
                response.success()
            else:
                response.failure(f"미션 {mission_id} 참가 실패: {response.status_code}")

    @task(12)
    def view_mission_tasks(self):
        """미션 태스크 조회 (중간 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        mission_id = random.choice(self.mission_ids)
        
        # 미션 태스크 목록 조회
        with self.client.get(f"/api/v1/missions/{mission_id}/tasks", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                tasks = data.get("data", [])
                
                # 태스크 개수 확인
                task_count = len(tasks)
                
                response.success()
            elif response.status_code == 404:
                # 태스크가 없는 미션이거나 존재하지 않는 미션
                response.success()
            else:
                response.failure(f"미션 {mission_id} 태스크 조회 실패: {response.status_code}")

    @task(10)
    def check_my_mission_progress(self):
        """내 미션 진행상황 확인 (중간 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        mission_id = random.choice(self.mission_ids)
        
        # 내 미션 태스크 조회
        with self.client.get(f"/api/v1/missions/{mission_id}/my-tasks", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                my_tasks = data.get("data", [])
                
                # 진행상황 분석
                total_tasks = len(my_tasks)
                completed_tasks = [task for task in my_tasks if task.get("status") == "COMPLETED"]
                completed_count = len(completed_tasks)
                
                response.success()
            elif response.status_code == 404:
                # 참가하지 않았거나 태스크가 없는 미션
                response.success()
            else:
                response.failure(f"미션 {mission_id} 내 태스크 조회 실패: {response.status_code}")

    @task(8)
    def detailed_mission_analysis(self):
        """미션 상세 분석 (낮은 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        mission_id = random.choice(self.mission_ids)
        
        # 미션 상세 정보 조회
        mission_data = None
        with self.client.get(f"/api/v1/missions/{mission_id}", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                mission_data = data.get("data", {})
                response.success()
            elif response.status_code == 404:
                response.success()
                return
            else:
                response.failure(f"미션 {mission_id} 상세 조회 실패: {response.status_code}")
                return
        
        # 챌린지 상태 확인
        with self.client.get(f"/api/v1/missions/{mission_id}/challenges", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                challenge_data = data.get("data", {})
                
                # 진행률 계산
                progress = challenge_data.get("progress", 0)
                status = challenge_data.get("status", "NOT_JOINED")
                
                response.success()
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"미션 {mission_id} 챌린지 상태 확인 실패: {response.status_code}")
        
        # 태스크 목록과 내 태스크 비교
        all_tasks = []
        my_tasks = []
        
        # 전체 태스크 조회
        with self.client.get(f"/api/v1/missions/{mission_id}/tasks", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                all_tasks = data.get("data", [])
                response.success()
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"미션 {mission_id} 전체 태스크 조회 실패: {response.status_code}")
        
        # 내 태스크 조회
        with self.client.get(f"/api/v1/missions/{mission_id}/my-tasks", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                my_tasks = data.get("data", [])
                response.success()
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"미션 {mission_id} 내 태스크 조회 실패: {response.status_code}")

    @task(5)
    def mission_completion_attempt(self):
        """미션 완료 시도 (낮은 빈도)"""
        if not self.access_token:
            return
            
        headers = self.get_headers()
        mission_id = random.choice(self.mission_ids)
        
        # 먼저 참가 상태 확인
        with self.client.get(f"/api/v1/missions/{mission_id}/challenges", headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                challenge_data = data.get("data", {})
                
                # 완료 가능한 상태인지 확인
                is_completable = challenge_data.get("isCompletable", False)
                
                if is_completable:
                    # 미션 완료 시도 (실제 API가 있다면)
                    # completion_data = {"completionNote": f"미션 완료 - {datetime.now().isoformat()}"}
                    # with self.client.post(f"/api/v1/missions/{mission_id}/complete", json=completion_data, headers=headers, catch_response=True) as complete_response:
                    #     if complete_response.status_code == 200:
                    #         complete_response.success()
                    #     else:
                    #         complete_response.failure(f"미션 {mission_id} 완료 실패: {complete_response.status_code}")
                    pass
                
                response.success()
            elif response.status_code == 404:
                response.success()
            else:
                response.failure(f"미션 {mission_id} 완료 확인 실패: {response.status_code}")

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
            elif response.status_code == 400:
                # 토큰이 아직 유효함
                response.success()
            else:
                response.failure(f"토큰 갱신 실패: {response.status_code}")


# 사용자 정의 이벤트 리스너
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=== HugmeEXP 미션 전용 부하테스트 시작 ===")
    print(f"목표 사용자 수: {environment.parsed_options.num_users}")
    print(f"spawn rate: {environment.parsed_options.spawn_rate}")
    print("🎯 미션 전용 테스트 시나리오:")
    print("- 미션 상세 조회 및 탐색")
    print("- 미션 참가 (챌린지)")
    print("- 미션 태스크 조회")
    print("- 미션 진행상황 확인")
    print("- 미션 완료 시도")
    print("- 사용자 인증 토큰 관리")
    print("========================================")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=== HugmeEXP 미션 전용 부하테스트 완료 ===")
    print("결과 파일:")
    print("- mission_test_stats.csv")
    print("- mission_test_failures.csv")
    print("- mission_test_exceptions.csv")
    print("- mission_test_stats_history.csv")
    print("==========================================")

# 명령줄 실행을 위한 설정
if __name__ == "__main__":
    import os
    # 기본 설정
    os.environ.setdefault('LOCUST_HOST', 'http://localhost:8081')
    os.environ.setdefault('LOCUST_USERS', '1000')  # 미션 테스트를 위한 적절한 사용자 수
    os.environ.setdefault('LOCUST_SPAWN_RATE', '1.67')  # 분당 100명 = 초당 1.67명
    os.environ.setdefault('LOCUST_RUN_TIME', '900s')  # 15분간 테스트
    
    # CSV 출력 설정
    os.environ.setdefault('LOCUST_CSV', 'mission_test')
    
    print("=" * 55)
    print("HugmeEXP 미션 전용 부하테스트 설정")
    print("=" * 55)
    print("환경 변수 설정:")
    print(f"LOCUST_HOST: {os.environ.get('LOCUST_HOST')}")
    print(f"LOCUST_USERS: {os.environ.get('LOCUST_USERS')} (최대 동시사용자)")
    print(f"LOCUST_SPAWN_RATE: {os.environ.get('LOCUST_SPAWN_RATE')} (분당 100명씩 증가)")
    print(f"LOCUST_RUN_TIME: {os.environ.get('LOCUST_RUN_TIME')} (15분간 미션 테스트)")
    print(f"LOCUST_CSV: {os.environ.get('LOCUST_CSV')}")
    print("=" * 55)
    print("🎯 미션 전용 테스트 특징:")
    print("- 미션 관련 API만 집중 테스트")
    print("- 실제 사용자 미션 참가 패턴 시뮬레이션")
    print("- 미션 진행상황 및 완료도 추적")
    print("- 태스크 기반 미션 관리 테스트")
    print("=" * 55)
    print("실행 방법:")
    print("python -m locust -f locustfile_mission_only.py --host=http://localhost:8081 --users=1000 --spawn-rate=1.67 --run-time=900s --csv=mission_test --headless")
    print("또는")
    print("./run_mission_test.sh (Linux/macOS)")
    print("run_mission_test.bat (Windows)")
    print("=" * 55) 