@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo ========================================
echo HugmeEXP 1000명 부하테스트 실행
echo ========================================
echo.

REM 1000명까지 빠르게 테스트하기 위한 설정
set "LOCUST_HOST=http://localhost:8081"
set "LOCUST_USERS=1000"
set "LOCUST_SPAWN_RATE=5"
set "LOCUST_RUN_TIME=900s"
set "LOCUST_CSV=stress_test_1000"

echo 1000명 테스트 설정:
echo - 서버 주소: %LOCUST_HOST%
echo - 최대 동시 사용자 수: %LOCUST_USERS%명
echo - 사용자 증가율: %LOCUST_SPAWN_RATE%명/초 (분당 300명)
echo - 실행 시간: %LOCUST_RUN_TIME% (15분)
echo - 1000명 도달 예상 시간: 약 3.3분
echo.

set /p choice="1000명 테스트를 시작하시겠습니까? (y/n): "
if /i "%choice%"=="n" (
    echo 테스트를 취소했습니다.
    pause
    exit /b 0
)

echo.
echo ========================================
echo 🚀 1000명 부하테스트 시작
echo ========================================
echo 서버 주소: %LOCUST_HOST%
echo 최대 동시 사용자 수: %LOCUST_USERS%명
echo 사용자 증가율: %LOCUST_SPAWN_RATE%명/초
echo 실행 시간: %LOCUST_RUN_TIME%
echo 결과 파일: %LOCUST_CSV%_*.csv
echo ========================================
echo.

REM Python 및 Locust 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    pause
    exit /b 1
)

python -c "import locust" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Locust가 설치되지 않았습니다.
    echo pip install locust 명령어로 설치해주세요.
    pause
    exit /b 1
)

echo 💪 시스템 리소스를 최대한 활용하여 1000명 테스트를 실행합니다...
echo 📊 실시간 진행 상황을 모니터링하세요.
echo.

REM 1000명까지 테스트 실행
python -m locust -f locustfile.py ^
    --host=%LOCUST_HOST% ^
    --users=%LOCUST_USERS% ^
    --spawn-rate=%LOCUST_SPAWN_RATE% ^
    --run-time=%LOCUST_RUN_TIME% ^
    --csv=%LOCUST_CSV% ^
    --headless ^
    --logfile=locust_1000_test.log

echo.
echo ========================================
echo ✅ 1000명 부하테스트 완료
echo ========================================
echo 결과 파일:
echo - %LOCUST_CSV%_stats.csv        (통계 요약)
echo - %LOCUST_CSV%_failures.csv     (실패 요약)  
echo - %LOCUST_CSV%_exceptions.csv   (예외 요약)
echo - %LOCUST_CSV%_stats_history.csv (시간별 통계)
echo - locust_1000_test.log          (상세 로그)
echo ========================================
echo.

REM 결과 요약 표시
if exist "%LOCUST_CSV%_stats.csv" (
    echo 📊 최종 통계 요약:
    echo ----------------------------------------
    findstr "Aggregated" "%LOCUST_CSV%_stats.csv"
    echo ----------------------------------------
    echo.
    
    if exist "%LOCUST_CSV%_failures.csv" (
        echo 📈 실패 요약:
        echo ----------------------------------------
        type "%LOCUST_CSV%_failures.csv"
        echo ----------------------------------------
    )
) else (
    echo ⚠️ 통계 파일이 생성되지 않았습니다.
)

echo.
echo 🎯 1000명 테스트가 완료되었습니다!
echo 💡 로그 파일(locust_1000_test.log)에서 상세한 진행 과정을 확인할 수 있습니다.
echo.
pause 