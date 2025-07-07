@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo ========================================
echo HugmeEXP 부하테스트 실행 (Windows)
echo ========================================
echo.

REM 기본 설정 (locustfile.py와 일치)
set "LOCUST_HOST=http://localhost:8081"
set "LOCUST_USERS=1000"
set "LOCUST_SPAWN_RATE=1.67"
set "LOCUST_RUN_TIME=900s"
set "LOCUST_CSV=stress_test"

REM 사용자 입력 받기
echo 기본 설정:
echo - 서버 주소: %LOCUST_HOST%
echo - 최대 동시 사용자 수: %LOCUST_USERS%명
echo - 사용자 증가율: %LOCUST_SPAWN_RATE%명/초 (분당 100명)
echo - 실행 시간: %LOCUST_RUN_TIME% (15분)
echo.

set /p choice="기본 설정으로 실행하시겠습니까? (y/n): "
if /i "%choice%"=="n" (
    echo.
    echo 사용자 정의 설정:
    set /p "input_host=서버 주소 입력 (기본: %LOCUST_HOST%): "
    set /p "input_users=최대 동시 사용자 수 입력 (기본: %LOCUST_USERS%): "
    set /p "input_spawn_rate=사용자 증가율 입력 (기본: %LOCUST_SPAWN_RATE%명/초, 분당 100명): "
    set /p "input_run_time=실행 시간 입력 (기본: %LOCUST_RUN_TIME%, 15분): "
    
    if not "!input_host!"=="" set "LOCUST_HOST=!input_host!"
    if not "!input_users!"=="" set "LOCUST_USERS=!input_users!"
    if not "!input_spawn_rate!"=="" set "LOCUST_SPAWN_RATE=!input_spawn_rate!"
    if not "!input_run_time!"=="" set "LOCUST_RUN_TIME=!input_run_time!"
)

echo.
echo ========================================
echo 부하테스트 시작
echo ========================================
echo 서버 주소: %LOCUST_HOST%
echo 최대 동시 사용자 수: %LOCUST_USERS%명
echo 사용자 증가율: %LOCUST_SPAWN_RATE%명/초 (분당 100명)
echo 실행 시간: %LOCUST_RUN_TIME% (15분)
echo 결과 파일: %LOCUST_CSV%_*.csv
echo ========================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python을 설치하고 PATH에 추가해주세요.
    pause
    exit /b 1
)

REM Locust 설치 확인
python -c "import locust" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Locust가 설치되지 않았습니다.
    set /p "install_choice=설치하시겠습니까? (y/n): "
    if /i "!install_choice!"=="y" (
        echo Locust 설치 중...
        pip install locust
    ) else (
        echo 설치를 취소했습니다.
        pause
        exit /b 1
    )
)

REM Locust 실행 (python -m locust 사용)
echo 🚀 부하테스트를 시작합니다...
echo.
python -m locust -f locustfile.py --host=%LOCUST_HOST% --users=%LOCUST_USERS% --spawn-rate=%LOCUST_SPAWN_RATE% --run-time=%LOCUST_RUN_TIME% --csv=%LOCUST_CSV% --headless

echo.
echo ========================================
echo 부하테스트 완료
echo ========================================
echo 결과 파일:
echo - %LOCUST_CSV%_stats.csv        (통계 요약)
echo - %LOCUST_CSV%_failures.csv     (실패 요약)
echo - %LOCUST_CSV%_exceptions.csv   (예외 요약)
echo - %LOCUST_CSV%_stats_history.csv (시간별 통계)
echo ========================================
echo.

REM 결과 파일 존재 여부 확인 및 표시
if exist "%LOCUST_CSV%_stats.csv" (
    echo 📊 통계 파일 내용 미리보기:
    echo ----------------------------------------
    type "%LOCUST_CSV%_stats.csv"
    echo ----------------------------------------
    echo.
    echo 📈 실패 요약:
    echo ----------------------------------------
    if exist "%LOCUST_CSV%_failures.csv" (
        type "%LOCUST_CSV%_failures.csv"
    ) else (
        echo 실패 기록이 없습니다. (모든 요청 성공)
    )
    echo ----------------------------------------
) else (
    echo ⚠️ 경고: 통계 파일이 생성되지 않았습니다.
)

echo.
echo ✅ 테스트 완료. 결과 파일을 확인하세요.
echo.
echo 💡 팁:
echo - 웹 UI로 실행하려면: python -m locust -f locustfile.py --host=%LOCUST_HOST%
echo - 브라우저에서 http://localhost:8089 접속
echo.
pause 