@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo ========================================
echo HugmeEXP 미션 전용 부하테스트 실행
echo ========================================
echo.

REM 미션 테스트 전용 설정
set "LOCUST_HOST=http://localhost:8081"
set "LOCUST_USERS=1000"
set "LOCUST_SPAWN_RATE=1.67"
set "LOCUST_RUN_TIME=900s"
set "LOCUST_CSV=mission_test"

echo 🎯 미션 전용 테스트 설정:
echo - 서버 주소: %LOCUST_HOST%
echo - 미션 테스터 수: %LOCUST_USERS%명
echo - 사용자 증가율: %LOCUST_SPAWN_RATE%명/초 (분당 100명)
echo - 실행 시간: %LOCUST_RUN_TIME% (15분간 미션 집중 테스트)
echo - 결과 파일: %LOCUST_CSV%_*.csv
echo.
echo 📋 테스트 시나리오:
echo   ✅ 미션 상세 조회 및 탐색 (높은 빈도)
echo   ✅ 미션 참가 및 챌린지 관리 (높은 빈도)
echo   ✅ 미션 태스크 조회 (중간 빈도)
echo   ✅ 미션 진행상황 확인 (중간 빈도)
echo   ✅ 미션 상세 분석 (낮은 빈도)
echo   ✅ 미션 완료 시도 (낮은 빈도)
echo.

set /p choice="미션 전용 테스트를 시작하시겠습니까? (y/n): "
if /i "%choice%"=="n" (
    echo 미션 테스트를 취소했습니다.
    pause
    exit /b 0
)

echo.
echo ========================================
echo 🚀 미션 전용 부하테스트 시작
echo ========================================
echo 서버 주소: %LOCUST_HOST%
echo 미션 테스터 수: %LOCUST_USERS%명
echo 사용자 증가율: %LOCUST_SPAWN_RATE%명/초
echo 실행 시간: %LOCUST_RUN_TIME%
echo 결과 파일: %LOCUST_CSV%_*.csv
echo ========================================
echo.

REM Python 및 Locust 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo 설치 방법: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 🐍 Python 버전: 
python --version

python -c "import locust" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Locust가 설치되지 않았습니다.
    set /p install="지금 설치하시겠습니까? (y/n): "
    if /i "!install!"=="y" (
        echo 📦 Locust 설치 중...
        pip install locust
        if %errorlevel% neq 0 (
            echo ❌ Locust 설치에 실패했습니다.
            pause
            exit /b 1
        )
        echo ✅ Locust 설치 완료
    ) else (
        echo 설치를 취소했습니다.
        pause
        exit /b 1
    )
)

echo 📊 Locust 버전:
python -m locust --version | head -1

REM locustfile_mission_only.py 존재 확인
if not exist "locustfile_mission_only.py" (
    echo ❌ locustfile_mission_only.py 파일이 없습니다.
    echo 현재 디렉토리에 미션 전용 locust 파일이 있는지 확인하세요.
    pause
    exit /b 1
)

echo.
echo 🎯 미션 API 집중 테스트를 시작합니다...
echo 📈 실시간 진행 상황:
echo - 미션 상세 조회: 매초 약 13회 (1000명 기준)
echo - 미션 참가 시도: 매초 약 10회  
echo - 태스크 조회: 매초 약 8회
echo - 진행상황 확인: 매초 약 7회
echo.

REM 미션 전용 테스트 실행
python -m locust -f locustfile_mission_only.py ^
    --host=%LOCUST_HOST% ^
    --users=%LOCUST_USERS% ^
    --spawn-rate=%LOCUST_SPAWN_RATE% ^
    --run-time=%LOCUST_RUN_TIME% ^
    --csv=%LOCUST_CSV% ^
    --headless

REM 실행 결과 확인
set TEST_EXIT_CODE=%errorlevel%

echo.
echo ========================================
echo 🎯 미션 전용 부하테스트 완료
echo ========================================
echo 결과 파일:
echo - %LOCUST_CSV%_stats.csv        (미션 API 통계)
echo - %LOCUST_CSV%_failures.csv     (미션 API 실패)
echo - %LOCUST_CSV%_exceptions.csv   (미션 API 예외)
echo - %LOCUST_CSV%_stats_history.csv (시간별 미션 통계)
echo ========================================
echo.

REM 결과 파일 존재 여부 확인 및 표시
if exist "%LOCUST_CSV%_stats.csv" (
    echo 📊 미션 테스트 통계 미리보기:
    echo ----------------------------------------
    echo 상위 10개 결과:
    for /f "skip=1 tokens=*" %%i in ('type "%LOCUST_CSV%_stats.csv" ^| head -10') do echo %%i
    echo ----------------------------------------
    echo.
    echo 📈 미션 API 실패 요약:
    echo ----------------------------------------
    if exist "%LOCUST_CSV%_failures.csv" (
        for /f %%i in ('find /c /v "" "%LOCUST_CSV%_failures.csv"') do set FAILURE_COUNT=%%i
        if !FAILURE_COUNT! GTR 1 (
            echo 실패 건수: !FAILURE_COUNT!개
            for /f "skip=1 tokens=*" %%i in ('type "%LOCUST_CSV%_failures.csv" ^| head -5') do echo %%i
        ) else (
            echo 미션 API 실패 없음! 모든 요청 성공 ✅
        )
    ) else (
        echo 실패 파일이 생성되지 않았습니다.
    )
    echo ----------------------------------------
) else (
    echo ⚠️ 경고: 통계 파일이 생성되지 않았습니다.
)

echo.
if %TEST_EXIT_CODE% equ 0 (
    echo ✅ 미션 전용 테스트가 성공적으로 완료되었습니다!
    echo.
    echo 📋 미션 테스트 요약:
    echo - 1000명의 가상 사용자가 미션 시스템을 테스트했습니다
    echo - 15분간 집중적으로 미션 API를 테스트했습니다
    echo - 미션 참가, 태스크 조회, 진행상황 확인을 검증했습니다
) else (
    echo ⚠️ 미션 테스트가 오류와 함께 완료되었습니다. (종료 코드: %TEST_EXIT_CODE%)
    echo 로그를 확인하여 문제를 해결해주세요.
)

echo.
echo 💡 추가 팁:
echo - 웹 UI로 실행: python -m locust -f locustfile_mission_only.py --host=%LOCUST_HOST%
echo - 브라우저에서 http://localhost:8089 접속하여 실시간 모니터링
echo - CSV 결과를 Excel로 열어서 미션 API 성능 분석 가능
echo - 실제 서버에서 테스트시 LOCUST_HOST를 변경하세요
echo.
pause 