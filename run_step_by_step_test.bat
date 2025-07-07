@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo ========================================
echo HugmeEXP 단계별 부하테스트 (1000명까지)
echo ========================================
echo.

set "LOCUST_HOST=http://localhost:8081"

echo 단계별 테스트 계획:
echo 1단계: 200명 동시 사용자 (3분)
echo 2단계: 500명 동시 사용자 (5분) 
echo 3단계: 1000명 동시 사용자 (15분)
echo.

set /p choice="단계별 테스트를 시작하시겠습니까? (y/n): "
if /i "%choice%"=="n" (
    echo 테스트를 취소했습니다.
    pause
    exit /b 0
)

echo.
echo ========================================
echo 🚀 1단계: 200명 테스트 시작
echo ========================================

python -m locust -f locustfile.py ^
    --host=%LOCUST_HOST% ^
    --users=200 ^
    --spawn-rate=3 ^
    --run-time=180s ^
    --csv=step1_200users ^
    --headless

echo.
echo ✅ 1단계 완료. 잠시 대기 중... (30초)
timeout /t 30 /nobreak

echo.
echo ========================================
echo 🚀 2단계: 500명 테스트 시작  
echo ========================================

python -m locust -f locustfile.py ^
    --host=%LOCUST_HOST% ^
    --users=500 ^
    --spawn-rate=4 ^
    --run-time=300s ^
    --csv=step2_500users ^
    --headless

echo.
echo ✅ 2단계 완료. 잠시 대기 중... (30초)
timeout /t 30 /nobreak

echo.
echo ========================================
echo 🚀 3단계: 1000명 테스트 시작
echo ========================================

python -m locust -f locustfile.py ^
    --host=%LOCUST_HOST% ^
    --users=1000 ^
    --spawn-rate=5 ^
    --run-time=900s ^
    --csv=step3_1000users ^
    --headless

echo.
echo ========================================
echo ✅ 모든 단계 완료!
echo ========================================
echo 결과 파일들:
echo - step1_200users_*.csv   (200명 테스트)
echo - step2_500users_*.csv   (500명 테스트)  
echo - step3_1000users_*.csv  (1000명 테스트)
echo ========================================
pause 