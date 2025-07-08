#!/bin/bash

# HugmeEXP 미션 전용 부하테스트 실행 스크립트 (Linux/macOS)
# 미션 관련 API만을 집중적으로 테스트합니다.

clear
echo "=========================================="
echo "HugmeEXP 미션 전용 부하테스트 실행"
echo "=========================================="
echo

# 미션 테스트 전용 설정
LOCUST_HOST=${LOCUST_HOST:-"http://localhost:8081"}
LOCUST_USERS=${LOCUST_USERS:-1000}
LOCUST_SPAWN_RATE=${LOCUST_SPAWN_RATE:-1.67}
LOCUST_RUN_TIME=${LOCUST_RUN_TIME:-"900s"}
LOCUST_CSV=${LOCUST_CSV:-"mission_test"}

echo "🎯 미션 전용 테스트 설정:"
echo "- 서버 주소: $LOCUST_HOST"
echo "- 미션 테스터 수: $LOCUST_USERS명"
echo "- 사용자 증가율: $LOCUST_SPAWN_RATE명/초 (분당 100명)"
echo "- 실행 시간: $LOCUST_RUN_TIME (15분간 미션 집중 테스트)"
echo "- 결과 파일: ${LOCUST_CSV}_*.csv"
echo
echo "📋 테스트 시나리오:"
echo "  ✅ 미션 상세 조회 및 탐색 (높은 빈도)"
echo "  ✅ 미션 참가 및 챌린지 관리 (높은 빈도)"
echo "  ✅ 미션 태스크 조회 (중간 빈도)"
echo "  ✅ 미션 진행상황 확인 (중간 빈도)"
echo "  ✅ 미션 상세 분석 (낮은 빈도)"
echo "  ✅ 미션 완료 시도 (낮은 빈도)"
echo

read -p "미션 전용 테스트를 시작하시겠습니까? (y/n): " choice
if [[ "$choice" == "n" || "$choice" == "N" ]]; then
    echo "미션 테스트를 취소했습니다."
    exit 0
fi

# 사용자 정의 설정 받기
read -p "설정을 변경하시겠습니까? (기본값 사용: Enter, 변경: y): " config_choice
if [[ "$config_choice" == "y" || "$config_choice" == "Y" ]]; then
    read -p "서버 주소 입력 (기본: $LOCUST_HOST): " input_host
    read -p "미션 테스터 수 입력 (기본: $LOCUST_USERS): " input_users
    read -p "사용자 증가율 입력 (기본: $LOCUST_SPAWN_RATE명/초): " input_spawn_rate
    read -p "실행 시간 입력 (기본: $LOCUST_RUN_TIME): " input_run_time
    
    # 입력값이 있으면 사용, 없으면 기본값 유지
    LOCUST_HOST=${input_host:-$LOCUST_HOST}
    LOCUST_USERS=${input_users:-$LOCUST_USERS}
    LOCUST_SPAWN_RATE=${input_spawn_rate:-$LOCUST_SPAWN_RATE}
    LOCUST_RUN_TIME=${input_run_time:-$LOCUST_RUN_TIME}
fi

echo
echo "=========================================="
echo "🚀 미션 전용 부하테스트 시작"
echo "=========================================="
echo "서버 주소: $LOCUST_HOST"
echo "미션 테스터 수: $LOCUST_USERS명"
echo "사용자 증가율: $LOCUST_SPAWN_RATE명/초"
echo "실행 시간: $LOCUST_RUN_TIME"
echo "결과 파일: ${LOCUST_CSV}_*.csv"
echo "=========================================="
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

echo "📊 Locust 버전: $($PYTHON_CMD -m locust --version | head -1)"

# locustfile_mission_only.py 존재 확인
if [[ ! -f "locustfile_mission_only.py" ]]; then
    echo "❌ locustfile_mission_only.py 파일이 없습니다."
    echo "현재 디렉토리에 미션 전용 locust 파일이 있는지 확인하세요."
    exit 1
fi

echo
echo "🎯 미션 API 집중 테스트를 시작합니다..."
echo "📈 실시간 진행 상황:"
echo "- 미션 상세 조회: 매초 약 13회 (1000명 기준)"
echo "- 미션 참가 시도: 매초 약 10회"  
echo "- 태스크 조회: 매초 약 8회"
echo "- 진행상황 확인: 매초 약 7회"
echo

# 미션 전용 부하테스트 실행
$PYTHON_CMD -m locust -f locustfile_mission_only.py \
    --host="$LOCUST_HOST" \
    --users="$LOCUST_USERS" \
    --spawn-rate="$LOCUST_SPAWN_RATE" \
    --run-time="$LOCUST_RUN_TIME" \
    --csv="$LOCUST_CSV" \
    --headless

# 실행 결과 확인
TEST_EXIT_CODE=$?

echo
echo "=========================================="
echo "🎯 미션 전용 부하테스트 완료"
echo "=========================================="
echo "결과 파일:"
echo "- ${LOCUST_CSV}_stats.csv        (미션 API 통계)"
echo "- ${LOCUST_CSV}_failures.csv     (미션 API 실패)"
echo "- ${LOCUST_CSV}_exceptions.csv   (미션 API 예외)"
echo "- ${LOCUST_CSV}_stats_history.csv (시간별 미션 통계)"
echo "=========================================="
echo

# 결과 파일 존재 여부 확인 및 표시
if [[ -f "${LOCUST_CSV}_stats.csv" ]]; then
    echo "📊 미션 테스트 통계 미리보기:"
    echo "----------------------------------------"
    echo "상위 10개 결과:"
    head -10 "${LOCUST_CSV}_stats.csv"
    echo "----------------------------------------"
    echo
    echo "📈 미션 API 실패 요약:"
    echo "----------------------------------------"
    if [[ -f "${LOCUST_CSV}_failures.csv" ]]; then
        FAILURE_COUNT=$(wc -l < "${LOCUST_CSV}_failures.csv")
        if [[ $FAILURE_COUNT -gt 1 ]]; then
            echo "실패 건수: $((FAILURE_COUNT-1))개"
            echo "상위 5개 실패:"
            head -6 "${LOCUST_CSV}_failures.csv" | tail -5
        else
            echo "미션 API 실패 없음! 모든 요청 성공 ✅"
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
    echo "✅ 미션 전용 테스트가 성공적으로 완료되었습니다!"
    echo
    echo "📋 미션 테스트 요약:"
    echo "- $LOCUST_USERS명의 가상 사용자가 미션 시스템을 테스트했습니다"
    echo "- ${LOCUST_RUN_TIME}간 집중적으로 미션 API를 테스트했습니다"
    echo "- 미션 참가, 태스크 조회, 진행상황 확인을 검증했습니다"
    
    # 간단한 성능 지표 계산
    if [[ -f "${LOCUST_CSV}_stats.csv" ]]; then
        echo
        echo "🔍 주요 성능 지표:"
        # CSV에서 총 요청 수와 실패 수 추출 (간단한 방법)
        if command -v awk &> /dev/null; then
            TOTAL_REQUESTS=$(awk -F',' 'NR>1 && $1!="Aggregated" {sum+=$2} END {print sum}' "${LOCUST_CSV}_stats.csv")
            TOTAL_FAILURES=$(awk -F',' 'NR>1 && $1!="Aggregated" {sum+=$3} END {print sum}' "${LOCUST_CSV}_stats.csv")
            
            if [[ ! -z "$TOTAL_REQUESTS" && "$TOTAL_REQUESTS" -gt 0 ]]; then
                SUCCESS_RATE=$(awk "BEGIN {printf \"%.2f\", (($TOTAL_REQUESTS-$TOTAL_FAILURES)/$TOTAL_REQUESTS)*100}")
                echo "- 총 요청 수: $TOTAL_REQUESTS"
                echo "- 실패 수: $TOTAL_FAILURES"
                echo "- 성공률: ${SUCCESS_RATE}%"
            fi
        fi
    fi
else
    echo "⚠️ 미션 테스트가 오류와 함께 완료되었습니다. (종료 코드: $TEST_EXIT_CODE)"
    echo "로그를 확인하여 문제를 해결해주세요."
fi

echo
echo "💡 추가 팁:"
echo "- 웹 UI로 실행: $PYTHON_CMD -m locust -f locustfile_mission_only.py --host=$LOCUST_HOST"
echo "- 브라우저에서 http://localhost:8089 접속하여 실시간 모니터링"
echo "- CSV 결과를 Excel이나 Google Sheets로 열어서 미션 API 성능 분석"
echo "- 실제 서버에서 테스트시 LOCUST_HOST를 변경하세요"
echo "- 더 긴 테스트: LOCUST_RUN_TIME=600s ./run_mission_test.sh"
echo "- 더 많은 사용자: LOCUST_USERS=500 ./run_mission_test.sh"
echo

# 추가 분석 도구 제안
echo "🔧 추가 분석 도구:"
echo "- 실시간 모니터링: watch -n 1 'tail -5 ${LOCUST_CSV}_stats_history.csv'"
echo "- 실패 분석: grep -v '^Method' ${LOCUST_CSV}_failures.csv | sort | uniq -c"
echo "- 평균 응답시간 확인: awk -F',' 'NR>1 {print \$1, \$5}' ${LOCUST_CSV}_stats.csv"
echo 