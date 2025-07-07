#!/bin/bash

# HugmeEXP 부하테스트 실행 스크립트 (Linux/macOS)
# 이 스크립트는 HugmeEXP 플랫폼에 대한 부하테스트를 수행합니다.

clear
echo "========================================"
echo "HugmeEXP 부하테스트 실행 (Linux/macOS)"
echo "========================================"
echo

# 기본 설정 (locustfile.py와 일치)
LOCUST_HOST=${LOCUST_HOST:-"http://localhost:8081"}
LOCUST_USERS=${LOCUST_USERS:-1000}
LOCUST_SPAWN_RATE=${LOCUST_SPAWN_RATE:-1.67}
LOCUST_RUN_TIME=${LOCUST_RUN_TIME:-"600s"}
LOCUST_CSV=${LOCUST_CSV:-"stress_test"}

# 사용자 입력 받기
echo "기본 설정:"
echo "- 서버 주소: $LOCUST_HOST"
echo "- 최대 동시 사용자 수: $LOCUST_USERS명"
echo "- 사용자 증가율: $LOCUST_SPAWN_RATE명/초 (분당 100명)"
echo "- 실행 시간: $LOCUST_RUN_TIME (10분)"
echo

read -p "기본 설정으로 실행하시겠습니까? (y/n): " choice
if [[ "$choice" == "n" || "$choice" == "N" ]]; then
    read -p "서버 주소 입력 (기본: $LOCUST_HOST): " input_host
    read -p "최대 동시 사용자 수 입력 (기본: $LOCUST_USERS): " input_users
    read -p "사용자 증가율 입력 (기본: $LOCUST_SPAWN_RATE명/초, 분당 100명): " input_spawn_rate
    read -p "실행 시간 입력 (기본: $LOCUST_RUN_TIME): " input_run_time
    
    # 입력값이 있으면 사용, 없으면 기본값 유지
    LOCUST_HOST=${input_host:-$LOCUST_HOST}
    LOCUST_USERS=${input_users:-$LOCUST_USERS}
    LOCUST_SPAWN_RATE=${input_spawn_rate:-$LOCUST_SPAWN_RATE}
    LOCUST_RUN_TIME=${input_run_time:-$LOCUST_RUN_TIME}
fi

echo
echo "========================================"
echo "부하테스트 시작"
echo "========================================"
echo "서버 주소: $LOCUST_HOST"
echo "최대 동시 사용자 수: $LOCUST_USERS명"
echo "사용자 증가율: $LOCUST_SPAWN_RATE명/초 (분당 100명)"
echo "실행 시간: $LOCUST_RUN_TIME (10분)"
echo "결과 파일: ${LOCUST_CSV}_*.csv"
echo "========================================"
echo

# Python 설치 확인
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python이 설치되지 않았습니다."
    echo "설치 방법:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

# Python 명령어 설정
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo "🐍 Python 버전: $($PYTHON_CMD --version)"

# Locust 설치 확인
if ! $PYTHON_CMD -c "import locust" &> /dev/null; then
    echo "❌ Locust가 설치되지 않았습니다."
    read -p "지금 설치하시겠습니까? (y/n): " install_choice
    if [[ "$install_choice" == "y" || "$install_choice" == "Y" ]]; then
        echo "📦 Locust 설치 중..."
        $PIP_CMD install locust
        if [ $? -ne 0 ]; then
            echo "❌ Locust 설치에 실패했습니다."
            echo "수동 설치: $PIP_CMD install locust"
            exit 1
        fi
        echo "✅ Locust 설치 완료"
    else
        echo "설치를 취소했습니다."
        exit 1
    fi
fi

# Locust 버전 확인
echo "📊 Locust 버전: $($PYTHON_CMD -m locust --version | head -1)"

# locustfile.py 존재 확인
if [[ ! -f "locustfile.py" ]]; then
    echo "❌ locustfile.py 파일이 없습니다."
    echo "현재 디렉토리에 locustfile.py가 있는지 확인하세요."
    exit 1
fi

# 부하테스트 실행
echo "🚀 부하테스트를 시작합니다..."
echo

$PYTHON_CMD -m locust -f locustfile.py \
    --host="$LOCUST_HOST" \
    --users="$LOCUST_USERS" \
    --spawn-rate="$LOCUST_SPAWN_RATE" \
    --run-time="$LOCUST_RUN_TIME" \
    --csv="$LOCUST_CSV" \
    --headless

# 실행 결과 확인
TEST_EXIT_CODE=$?

echo
echo "========================================"
echo "부하테스트 완료"
echo "========================================"
echo "결과 파일:"
echo "- ${LOCUST_CSV}_stats.csv        (통계 요약)"
echo "- ${LOCUST_CSV}_failures.csv     (실패 요약)"
echo "- ${LOCUST_CSV}_exceptions.csv   (예외 요약)"
echo "- ${LOCUST_CSV}_stats_history.csv (시간별 통계)"
echo "========================================"
echo

# 결과 파일 존재 여부 확인 및 표시
if [[ -f "${LOCUST_CSV}_stats.csv" ]]; then
    echo "📊 통계 파일 내용 미리보기:"
    echo "----------------------------------------"
    head -10 "${LOCUST_CSV}_stats.csv"
    echo "----------------------------------------"
    echo
    echo "📈 실패 요약:"
    echo "----------------------------------------"
    if [[ -f "${LOCUST_CSV}_failures.csv" ]]; then
        if [[ -s "${LOCUST_CSV}_failures.csv" ]]; then
            head -10 "${LOCUST_CSV}_failures.csv"
        else
            echo "실패 기록이 없습니다. (모든 요청 성공) ✅"
        fi
    else
        echo "실패 파일이 생성되지 않았습니다."
    fi
    echo "----------------------------------------"
else
    echo "⚠️ 경고: 통계 파일이 생성되지 않았습니다."
fi

echo
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ 테스트가 성공적으로 완료되었습니다."
else
    echo "⚠️ 테스트가 오류와 함께 완료되었습니다. (종료 코드: $TEST_EXIT_CODE)"
fi

echo
echo "💡 팁:"
echo "- 웹 UI로 실행하려면: $PYTHON_CMD -m locust -f locustfile.py --host=$LOCUST_HOST"
echo "- 브라우저에서 http://localhost:8089 접속"
echo "- CSV 파일을 Excel이나 Google Sheets로 열어서 상세 분석 가능"
echo 