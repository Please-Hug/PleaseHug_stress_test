# HugmeEXP 부하테스트

HugmeEXP 교육 플랫폼에 대한 종합적인 부하테스트를 수행하기 위한 Locust 테스트 스크립트입니다.

## 📋 테스트 대상 API

이 부하테스트는 HugmeEXP 플랫폼의 다음 API들을 테스트합니다:

### 🔐 인증 시스템
- 사용자 회원가입/로그인
- JWT 토큰 갱신
- 로그아웃

### 👤 사용자 관리
- 프로필 조회/수정
- 리더보드 조회
- 사용자별 통계

### 📚 교육 기능
- **미션**: 목록 조회, 상세 조회, 참가
- **배움일기**: 생성, 목록 조회, 검색, 상세 조회
- **퀘스트**: 일일 퀘스트 조회 및 완료
- **출석**: 출석 체크, 상태 조회

### 🛒 포인트 시스템
- 상품 목록 조회
- 상품 구매
- 주문 내역 조회

### 💬 소셜 기능
- **칭찬**: 칭찬 생성, 검색, 인기 칭찬 조회
- **북마크**: 북마크 CRUD
- **댓글**: 댓글 작성 및 관리

### 📁 파일 관리
- 이미지 업로드
- 파일 다운로드

## 🎯 테스트 시나리오

### 사용자 행동 패턴
테스트는 실제 사용자의 행동 패턴을 시뮬레이션합니다:

1. **로그인 및 출석 체크** (높은 빈도 - @task(10))
2. **미션 탐색 및 참가** (높은 빈도 - @task(12))
3. **배움일기 조회** (높은 빈도 - @task(15))
4. **프로필 확인** (중간 빈도 - @task(8))
5. **퀘스트 완료** (중간 빈도 - @task(6))
6. **샵 상품 탐색** (중간 빈도 - @task(7))
7. **칭찬 활동** (중간 빈도 - @task(8))
8. **컨텐츠 생성** (낮은 빈도 - @task(2-5))

### 동시 접속자
- **기본 설정**: 100명의 동시 접속자
- **증가율**: 초당 10명씩 증가
- **테스트 시간**: 5분 (300초)

## 🚀 실행 방법

### 필요 조건
```bash
# Python 환경 설정
pip install locust

# 또는 requirements.txt 사용
pip install -r requirements.txt
```

### 1. 전체 시스템 테스트
전체 플랫폼에 대한 종합적인 부하테스트를 실행합니다.

#### Windows에서 실행
```bash
run_test.bat
```

#### Linux/macOS에서 실행
```bash
chmod +x run_test.sh
./run_test.sh
```

### 2. 🎯 미션 전용 테스트 (신규!)
미션 관련 API만을 집중적으로 테스트하는 전용 스크립트입니다.

#### Windows에서 실행
```bash
run_mission_test.bat
```

#### Linux/macOS에서 실행
```bash
chmod +x run_mission_test.sh
./run_mission_test.sh
```

#### 미션 전용 테스트 특징
- **타겟 API**: 미션 조회, 참가, 태스크 관리 등
- **테스트 시간**: 15분 (기본값)
- **동시 사용자**: 1000명 (기본값)
- **증가율**: 분당 100명씩 점진적 증가
- **결과 파일**: `mission_test_*.csv`

### 3. 직접 실행

#### 전체 시스템 테스트
```bash
# 기본 설정으로 실행
locust -f locustfile.py --host=http://localhost:8081 --users=1000 --spawn-rate=1.67 --run-time=600s --csv=stress_test --headless

# 웹 UI로 실행 (수동 설정)
locust -f locustfile.py --host=http://localhost:8081
# 브라우저에서 http://localhost:8089 접속
```

#### 미션 전용 테스트
```bash
# 미션 전용 테스트 실행
locust -f locustfile_mission_only.py --host=http://localhost:8081 --users=1000 --spawn-rate=1.67 --run-time=900s --csv=mission_test --headless

# 미션 전용 웹 UI
locust -f locustfile_mission_only.py --host=http://localhost:8081
# 브라우저에서 http://localhost:8089 접속
```

### 4. 환경변수로 설정
```bash
export LOCUST_HOST=http://your-server:8080
export LOCUST_USERS=200
export LOCUST_SPAWN_RATE=20
export LOCUST_RUN_TIME=600s
./run_test.sh
```

## 📊 결과 분석

### 생성되는 파일
테스트 완료 후 다음 CSV 파일들이 생성됩니다:

- `stress_test_stats.csv`: 전체 요청 통계
- `stress_test_failures.csv`: 실패한 요청 목록
- `stress_test_exceptions.csv`: 발생한 예외 목록
- `stress_test_stats_history.csv`: 시간별 통계 기록

### 주요 메트릭
- **RPS (Requests Per Second)**: 초당 처리 요청 수
- **응답시간**: 평균/최소/최대 응답 시간
- **성공률**: 성공한 요청의 비율
- **동시 사용자 수**: 실제 활성 사용자 수

### 성능 기준
다음 기준을 목표로 합니다:

| 메트릭 | 목표 | 경고 |
|--------|------|------|
| 평균 응답시간 | < 500ms | > 1000ms |
| 95% 응답시간 | < 1000ms | > 2000ms |
| 에러율 | < 1% | > 5% |
| RPS | > 200 | < 100 |

## 🔧 커스터마이징

### 테스트 시나리오 수정
`locustfile.py`에서 `@task` 데코레이터의 숫자를 변경하여 작업 빈도를 조절할 수 있습니다:

```python
@task(20)  # 높은 빈도
def high_frequency_task(self):
    pass

@task(1)   # 낮은 빈도
def low_frequency_task(self):
    pass
```

### 테스트 데이터 수정
사용자 생성 패턴이나 테스트 데이터를 수정하려면:

```python
# 사용자명 패턴 변경
username = f"customuser{random.randint(1000, 9999)}"

# 테스트 데이터 패턴 변경
diary_data = {
    "title": f"Custom Title {random.randint(1, 1000)}",
    "content": "Custom content...",
}
```

### 서버 설정 변경
기본 서버 주소를 변경하려면:

```python
# locustfile.py 맨 아래
os.environ.setdefault('LOCUST_HOST', 'http://your-server:8080')
```

## 🐛 문제 해결

### 일반적인 문제들

**1. 연결 오류**
```
ConnectionError: HTTPConnectionPool
```
- 서버 주소 확인
- 서버가 실행 중인지 확인
- 방화벽 설정 확인

**2. 인증 오류**
```
401 Unauthorized
```
- 토큰 만료: 자동으로 재시도됨
- 잘못된 자격증명: 테스트 계정 확인

**3. 높은 에러율**
- 서버 용량 초과: 동시 사용자 수 감소
- 데이터베이스 연결 문제: DB 설정 확인
- 메모리 부족: 서버 리소스 확인

### 디버깅 모드
상세한 로그를 보려면:

```bash
locust -f locustfile.py --host=http://localhost:8080 --loglevel=DEBUG
```

## 📈 성능 최적화 팁

### 서버 측
1. **데이터베이스 최적화**
   - 인덱스 추가
   - 쿼리 최적화
   - 커넥션 풀 설정

2. **캐싱 적용**
   - Redis 캐시
   - CDN 사용
   - 정적 리소스 캐싱

3. **서버 설정**
   - JVM 메모리 설정
   - 스레드 풀 크기 조정
   - 로드 밸런싱

### 테스트 측
1. **점진적 증가**
   - 사용자 수를 천천히 증가
   - 서버 반응 관찰

2. **실제 환경 시뮬레이션**
   - 다양한 네트워크 조건
   - 실제 데이터 크기 사용

## 📋 요구사항

### Python 패키지
```
locust>=2.0.0
requests>=2.25.0
```

### 시스템 요구사항
- Python 3.7+
- 메모리: 최소 4GB (대규모 테스트시 8GB+ 권장)
- CPU: 멀티코어 권장

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해 주세요. 