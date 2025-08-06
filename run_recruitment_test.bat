@echo off
chcp 65001 > nul
echo ===============================================
echo Recruitment API Stress Test
echo ===============================================

echo.
echo 1. Normal Test (100 users, 10/sec spawn rate)
echo 2. Load Test (500 users, 50/sec spawn rate)
echo 3. Bottleneck Test (2000 users, 3/sec spawn rate)
echo 4. Web UI Mode
echo.

set /p choice=Select test type (1-4):

if "%choice%"=="1" (
    echo Starting normal test...
    locust -f locustfile_recruitment_test.py RecruitmentApiUser --host=http://localhost:8080 --users=100 --spawn-rate=10 --run-time=5m --html=recruitment_test_report.html
) else if "%choice%"=="2" (
    echo Starting load test...
    locust -f locustfile_recruitment_test.py RecruitmentApiLoadTest --host=http://localhost:8080 --users=500 --spawn-rate=50 --run-time=10m --html=recruitment_load_test_report.html
) else if "%choice%"=="3" (
    echo Starting bottleneck test...
    locust -f locustfile_recruitment_test.py RecruitmentApiUser --host=http://localhost:8080 --users=2000 --spawn-rate=3 --run-time=15m --html=recruitment_bottleneck_test_report.html
) else if "%choice%"=="4" (
    echo Starting Web UI... Open http://localhost:8089 in browser
    locust -f locustfile_recruitment_test.py RecruitmentApiUser --host=http://localhost:8080
) else (
    echo Invalid selection.
    goto :eof
)

echo.
echo Test completed! Check the report files.
pause
