@echo off
chcp 65001 >nul
title Auto Content Site - 一键部署到 GitHub

echo ==============================================
echo   Auto Content Site - 一键部署
echo ==============================================
echo.

:: 检查 git
where git >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Git！请先安装: https://git-scm.com/downloads
    pause
    exit /b
)
echo [OK] Git 已安装

:: 读取配置
set /p GITHUB_USER=GitHub 用户名:
set /p REPO_NAME=仓库名 (直接回车默认 auto-content-site):
if "%REPO_NAME%"=="" set REPO_NAME=auto-content-site

:: 检查 deploy.sh 是否存在
if not exist "%~dp0deploy.sh" (
    echo [!] 未找到 deploy.sh 脚本
    echo     请确保你在正确的目录下运行
    pause
    exit /b
)

:: 显示部署指引
echo.
echo ==============================================
echo   部署步骤：
echo ==============================================
echo.
echo   1. 打开 https://github.com/new 创建新仓库
echo      仓库名: %REPO_NAME%
echo      选 Public，不要勾选任何选项
echo.
echo   2. 在本目录打开终端，执行：
echo.
echo      git init -b main
echo      git add .
echo      git commit -m "初始化自动内容站"
echo      git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
echo      git push -u origin main
echo.
echo   3. 在 GitHub 仓库 Settings ^> Secrets and variables ^> Actions 添加:
echo      Name: DEEPSEEK_API_KEY
echo      Value: 你的 DeepSeek API Key (https://platform.deepseek.com)
echo.
echo   4. 在 GitHub 仓库 Settings ^> Pages 中:
echo      Source 选 "GitHub Actions"
echo.
echo   5. 搞定！每天早上8点自动发布新文章
echo      网站地址: https://%GITHUB_USER%.github.io/%REPO_NAME%
echo.
echo ==============================================
echo.
echo  也可以直接用 GitHub CLI 一键部署:
echo.
echo      gh repo create %REPO_NAME% --public --source=. --remote=origin --push
echo.
echo ==============================================

pause
