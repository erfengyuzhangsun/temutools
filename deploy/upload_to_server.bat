@echo off
chcp 65001 >nul
echo ==========================================
echo   Temu 运营平台 - 代码上传工具
echo   目标服务器: 请输入服务器IP或域名
echo ==========================================
echo.

if "%1"=="" (
    set /p SERVER_IP=请输入服务器IP地址或域名: 
) else (
    set SERVER_IP=%1
)

set SERVER_USER=root
set REMOTE_DIR=/opt/temu_tools
set LOCAL_DIR=d:\develop\code\temu_tools

echo 📂 本地目录: %LOCAL_DIR%
echo 🌐 远程目录: %REMOTE_DIR%
echo 🖥️  服务器: %SERVER_IP%
echo.
echo ⏳ 开始上传代码到服务器...
echo    (首次连接需要确认主机指纹，请输入 yes)
echo.

scp -r -o StrictHostKeyChecking=accept-new "%LOCAL_DIR%"* %SERVER_USER%@%SERVER_IP%:%REMOTE_DIR%/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 上传成功！
    echo.
    echo 下一步操作:
    echo   1. SSH登录服务器: ssh root@%SERVER_IP%
    echo   2. 运行部署: cd /opt/temu_tools ^&^& bash deploy_aliyun.sh
) else (
    echo.
    echo ❌ 上传失败，请检查:
    echo   - 网络连接是否正常
    echo   - 密码是否正确
    echo   - 服务器磁盘空间是否充足
)

pause
