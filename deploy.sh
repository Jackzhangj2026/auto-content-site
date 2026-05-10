#!/bin/bash
"""
====================================================
  Auto Content Site - 一键部署脚本
  本脚本会自动完成本地 Git 初始化 + GitHub 仓库创建
  你需要提前准备好: GitHub 账号 + Personal Access Token
====================================================
"""

set -e

echo "=============================================="
echo "  Auto Content Site - 一键部署"
echo "=============================================="
echo ""

# ---- 检查 git ----
if ! command -v git &> /dev/null; then
    echo "[错误] 请先安装 Git: https://git-scm.com/downloads"
    exit 1
fi

# ---- 检查 GitHub CLI 或 Token ----
HAS_GH=false
if command -v gh &> /dev/null; then
    HAS_GH=true
fi

if [ "$HAS_GH" = true ]; then
    echo "[✓] 检测到 GitHub CLI"
    if ! gh auth status &> /dev/null; then
        echo "    请先登录: gh auth login"
        exit 1
    fi
    echo "[✓] GitHub CLI 已登录"
else
    echo "[!] 未检测到 GitHub CLI"
    echo "    安装方式:"
    echo "      Mac:  brew install gh"
    echo "      Windows:  winget install GitHub.cli"
    echo "      Linux:  sudo apt install gh"
    echo ""
    echo "    或者手动创建仓库（见脚本末尾的说明）"
    echo ""
fi

# ---- 读取配置 ----
read -p "GitHub 用户名: " GITHUB_USER
read -p "仓库名称 (默认: auto-content-site): " REPO_NAME
REPO_NAME=${REPO_NAME:-auto-content-site}
read -p "网站标题 (默认: AI产品观察): " SITE_TITLE
SITE_TITLE=${SITE_TITLE:-AI产品观察}

# ---- 配置 _config.yml ----
echo ""
echo "[...] 配置网站信息..."
sed -i "s/title:.*/title: $SITE_TITLE/" _config.yml
sed -i "s|url:.*|url: https://$GITHUB_USER.github.io|" _config.yml
echo "[✓] 网站配置已更新"

# ---- 初始化 Git ----
if [ ! -d ".git" ]; then
    echo "[...] 初始化 Git 仓库..."
    git init
    echo "[✓] Git 初始化完成"
fi

# ---- 创建 GitHub 仓库 ----
if [ "$HAS_GH" = true ]; then
    echo "[...] 创建 GitHub 仓库..."

    # 检查仓库是否已存在
    if gh repo view "$GITHUB_USER/$REPO_NAME" &> /dev/null; then
        echo "[!] 仓库 $GITHUB_USER/$REPO_NAME 已存在，跳过创建"
    else
        gh repo create "$REPO_NAME" --public --description "全自动内容站：$SITE_TITLE" --remote origin
        echo "[✓] GitHub 仓库已创建"
    fi

    # 设置远程
    git remote set-url origin "https://github.com/$GITHUB_USER/$REPO_NAME.git" 2>/dev/null || \
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
else
    echo ""
    echo "=============================================="
    echo "  请手动在 GitHub 上创建仓库:"
    echo "  1. 打开 https://github.com/new"
    echo "  2. 仓库名: $REPO_NAME"
    echo "  3. 选 Public"
    echo "  4. 不要勾选任何初始化选项"
    echo "  5. 点击 Create repository"
    echo ""
    echo "  然后运行以下命令:"
    echo "    git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo "=============================================="
    echo ""
    read -p "按回车键继续（仓库创建完成后）..."
fi

# ---- 首次提交 ----
echo "[...] 提交代码..."
git add -A
git commit -m "🎉 初始化：自动内容站 - $SITE_TITLE" 2>/dev/null || echo "[!] 无变更需要提交"

# ---- 推送到 GitHub ----
echo "[...] 推送到 GitHub..."
git branch -M main
git push -u origin main 2>/dev/null || {
    echo ""
    echo "=============================================="
    echo "  [!] 推送失败，常见原因:"
    echo "  1. Token 权限不够 -> 在 GitHub Settings > Developer settings"
    echo "     > Personal access tokens 创建新 token，勾选 repo 权限"
    echo "  2. 远程仓库地址不对 -> git remote set-url origin ..."
    echo "=============================================="
    exit 1
}
echo "[✓] 代码已推送到 GitHub"

# ---- 配置 GitHub Pages ----
echo ""
echo "=============================================="
echo "  下一步：启用 GitHub Pages"
echo "=============================================="
echo ""
echo "  1. 打开 https://github.com/$GITHUB_USER/$REPO_NAME/settings/pages"
echo "  2. Source 选: GitHub Actions"
echo "  3. 或者选: Deploy from a branch -> main -> / (root)"
echo ""
echo "  GitHub Actions 会在每天早上自动运行"
echo "  你可以在 Actions 页面查看运行状态:"
echo "  https://github.com/$GITHUB_USER/$REPO_NAME/actions"
echo ""

# ---- 配置 DeepSeek API Key ----
echo "=============================================="
echo "  最后一步：配置 AI API Key"
echo "=============================================="
echo ""
echo "  推荐用 DeepSeek（新用户500万免费token）:"
echo ""
echo "  1. 注册: https://platform.deepseek.com/sign_up"
echo "  2. 登录后创建 API Key"
echo "  3. 在 GitHub 仓库设置中添加 Secret:"
echo "     https://github.com/$GITHUB_USER/$REPO_NAME/settings/secrets/actions"
echo "     Name: DEEPSEEK_API_KEY"
echo "     Value: 你复制的 API Key"
echo ""
echo "  不配也没关系，系统会自动用备用模板生成文章"
echo "  但配了 API Key 后文章质量会大幅提升"
echo ""

echo "=============================================="
echo "  ✅ 部署完成！"
echo "=============================================="
echo ""
echo "  网站地址: https://$GITHUB_USER.github.io/$REPO_NAME"
echo "  你的网站每天会自动更新一篇文章"
echo ""

# ---- 本地测试 ----
echo "你想现在本地测试一下吗？(y/n)"
read -p "> " TEST_NOW
if [ "$TEST_NOW" = "y" ] || [ "$TEST_NOW" = "Y" ]; then
    echo "[...] 本地测试..."
    python3 content_generator.py
    echo "[✓] 测试完成，生成的帖子在 _posts/ 目录下"
    echo "    你可以用浏览器打开 index.md 查看效果"
fi

echo ""
echo "🎉 一切就绪！等着流量和收入来吧！"
