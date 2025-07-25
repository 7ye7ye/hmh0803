@echo off
echo 正在检查8080端口是否被占用...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    set PID=%%a
    goto :found
)
goto :notfound

:found
echo 发现8080端口被PID=%PID%占用，正在尝试关闭...
taskkill /F /PID %PID%
if %ERRORLEVEL% EQU 0 (
    echo 成功关闭占用8080端口的进程
) else (
    echo 无法关闭占用8080端口的进程，请手动关闭后再试
    pause
    exit
)
goto :start

:notfound
echo 8080端口未被占用，可以直接启动

:start
echo 正在启动Vue开发服务器...
npm run serve

pause
