#!/usr/bin/env python3
"""
Auto Content Generator - 全自动内容生成器
每天定时运行，自动生成SEO优化文章并发布到GitHub Pages

支持多个AI后端（免费优先）：
1. DeepSeek API (新用户500万免费token)
2. OpenAI 兼容接口
3. 本地模型（需要自行配置）
"""

import os
import json
import random
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# 配置区 - 按需修改
# ============================================================

# 网站配置
SITE_TITLE = "AI产品观察"
SITE_DESCRIPTION = "聚焦AI时代的产品思维、工具评测与行业洞察"
SITE_LANGUAGE = "zh-CN"  # zh-CN 或 en

# 文章目录（相对于脚本位置）
POSTS_DIR = "_posts"

# 关键词文件（每行一个关键词或话题）
KEYWORDS_FILE = "keywords.txt"

# ============================================================
# AI API 配置 - 只用一个就行，优先用免费的
# ============================================================

# 方式1: DeepSeek API（推荐 - 免费的500万token）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 方式2: OpenAI 兼容接口（如 OneAPI, API2D 等）
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_API_URL = os.environ.get("OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

# ============================================================
# 领域知识 - 自动生成专业内容的基础
# ============================================================

# 默认中文关键词（可以根据你的领域修改）
DEFAULT_KEYWORDS_ZH = [
    # AI 产品方向
    "AI产品经理必备技能",
    "2026年AI工具推荐",
    "ChatGPT最新使用技巧",
    "AI绘画工具对比评测",
    "AI自动化工作流",
    "大模型应用落地实践",
    "AI Agent 开发入门",
    "AI写作工具推荐",
    "AI编程助手对比",
    "AI视频生成工具评测",

    # 产品管理方向
    "产品经理面试指南",
    "B端产品设计原则",
    "用户增长策略分析",
    "A/B测试最佳实践",
    "产品需求文档写法",
    "SaaS产品指标分析",
    "用户体验优化方法",
    "产品路线图规划",
    "数据分析驱动产品决策",
    "产品经理常用工具",

    # 电商/京东方向
    "京东电商运营策略",
    "电商数据分析方法",
    "电商产品管理要点",
    "供应链数字化趋势",
    "电商用户体验优化",
    "跨境电商选品策略",
    "电商平台算法解读",
    "电商促销策略分析",
]

# 默认英文关键词
DEFAULT_KEYWORDS_EN = [
    "AI product management skills",
    "Best AI tools 2026",
    "ChatGPT tips and tricks",
    "AI writing tools comparison",
    "Machine learning for beginners",
    "Product manager interview guide",
    "SaaS metrics guide",
    "User growth strategies",
    "A/B testing best practices",
    "Digital product design principles",
]

def get_keywords():
    """从关键词文件读取话题，如果没有则使用默认值"""
    if os.path.exists(KEYWORDS_FILE):
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            keywords = [line.strip() for line in f if line.strip()]
        if keywords:
            return keywords

    # 使用默认关键词
    if SITE_LANGUAGE.startswith("zh"):
        return DEFAULT_KEYWORDS_ZH
    else:
        return DEFAULT_KEYWORDS_EN


def generate_with_deepseek(prompt, temperature=0.8, max_tokens=3000):
    """使用 DeepSeek API 生成内容（免费）"""
    import urllib.request
    import urllib.error

    if not DEEPSEEK_API_KEY:
        return None

    payload = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的科技博客作者，擅长写深度、实用的文章。文章要结构清晰、有实际案例和数据支撑。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    })

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=payload.encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"DeepSeek API 调用失败: {e}")
        return None


def generate_with_openai(prompt, temperature=0.8, max_tokens=3000):
    """使用 OpenAI 兼容接口生成内容"""
    import urllib.request
    import urllib.error

    if not OPENAI_API_KEY:
        return None

    payload = json.dumps({
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "你是一个专业的科技博客作者，擅长写深度、实用的文章。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    })

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    req = urllib.request.Request(
        OPENAI_API_URL,
        data=payload.encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenAI API 调用失败: {e}")
        return None


def generate_article(keyword, publish_date):
    """生成一篇完整的文章"""
    print(f"正在生成文章: [{keyword}] 日期: {publish_date}")

    current_year = datetime.now().year

    # 根据语言构建不同的 prompt
    if SITE_LANGUAGE.startswith("zh"):
        prompt = f"""请以资深行业专家的身份，写一篇关于「{keyword}」的深度文章。

要求：
1. 标题：吸引人且包含 SEO 关键词，控制在15-25字
2. 字数：800-1500字
3. 结构：
   - 引人入胜的开头（点明痛点或趋势）
   - 2-3个核心论点（每个论点配一个实际案例或数据）
   - 实用建议/行动指南
   - 总结
4. 风格：专业但不晦涩，有实际干货
5. 适当使用小标题、列表来提升可读性
6. 如有数据，请使用 {current_year} 年或最新的行业数据

请按以下格式输出：
---
标题: [文章标题]
描述: [SEO描述，不超过100字]
分类: [所属分类]
标签: [标签1, 标签2, 标签3]
---

[正文内容]"""
    else:
        prompt = f"""Write a well-researched article about "{keyword}" in English.

Requirements:
1. Title: SEO-optimized, engaging, 40-60 characters
2. Length: 800-1500 words
3. Structure:
   - Compelling introduction (problem/trend hook)
   - 2-3 core arguments (each with real examples or data)
   - Practical tips/actionable advice
   - Conclusion
4. Style: Professional yet accessible, focus on practical value
5. Use subheadings and lists for readability
6. Use {current_year} data where relevant

Output format:
---
title: [Article Title]
description: [SEO description, max 160 chars]
category: [Category]
tags: [tag1, tag2, tag3]
---

[Article body]"""

    # 尝试用 DeepSeek 生成
    content = generate_with_deepseek(prompt)
    if content:
        return content

    # 如果 DeepSeek 失败，尝试 OpenAI 兼容接口
    content = generate_with_openai(prompt)
    if content:
        return content

    # 如果所有 API 都失败，使用模板生成（保证系统可用）
    return generate_fallback_article(keyword)


def generate_fallback_article(keyword):
    """备用方案：当 API 不可用时生成模板文章"""
    today = datetime.now().strftime("%Y-%m-%d")

    title = f"深入解析 {keyword}：2026年最新实践指南"
    description = f"全面了解{keyword}的最新趋势、最佳实践和实用技巧，帮助你在实际工作中快速应用。"
    category = "AI工具"
    tags = keyword

    body = f"""
## 为什么 {keyword} 如此重要？

在当今快速发展的技术环境中，{keyword} 已经成为各行各业关注的焦点。无论你是产品经理、开发者还是业务负责人，理解这一领域都将为你带来显著的竞争优势。

## 核心要点

### 1. 行业趋势

{keyword} 正在经历快速变革。2026年，我们看到了几个重要的发展方向：
- 技术门槛不断降低，更多人能够参与其中
- 应用场景从单一向多元化扩展
- 用户对体验和效果的要求越来越高

### 2. 最佳实践

要在 {keyword} 领域取得成功，以下实践值得关注：

**数据驱动决策**
在任何决策过程中，让数据说话是最可靠的方式。通过建立完善的数据收集和分析体系，你可以做出更准确的判断。

**用户中心思维**
无论技术如何发展，始终将用户需求放在首位。最好的产品往往不是技术最先进的，而是最懂用户的。

**持续迭代优化**
不要追求一次性完美，而是通过快速迭代不断改进。MVP（最小可行产品）思维在这一领域同样适用。

### 3. 实用工具推荐

以下是当前市场上值得关注的工具和平台：
1. 工具一：功能强大，适合专业用户
2. 工具二：操作简单，适合新手入门
3. 工具三：性价比高，适合中小企业

## 实施建议

如果你计划在 {keyword} 领域开始实践，建议按以下步骤进行：

1. **学习基础知识** - 花时间系统学习核心概念
2. **从小处着手** - 选择一个具体的切入点开始实践
3. **建立反馈循环** - 及时收集反馈并调整策略
4. **持续学习** - 保持对行业动态的关注

## 总结

{keyword} 是一个充满机遇的领域。通过系统学习和持续实践，你将能够在这一领域建立自己的核心竞争力。记住，最重要的不是知道所有答案，而是提出正确的问题。

---
*本文由 AI 辅助生成，仅供参考和学习使用。*
"""

    return f"""---
title: {title}
description: {description}
date: {today}
category: {category}
tags: {tags}
---

{body}"""


def parse_article_output(content, keyword, publish_date):
    """解析 AI 输出的文章内容"""
    date_str = publish_date.strftime("%Y-%m-%d")

    # 尝试从内容中解析 frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            body = parts[2].strip()

            # 解析 frontmatter
            title = None
            description = ""
            category = "默认分类"
            tags = keyword

            for line in frontmatter.strip().split("\n"):
                if line.startswith("标题:"):
                    title = line.split(":", 1)[1].strip()
                elif line.startswith("title:"):
                    title = line.split(":", 1)[1].strip()
                elif line.startswith("描述:"):
                    description = line.split(":", 1)[1].strip()
                elif line.startswith("description:"):
                    description = line.split(":", 1)[1].strip()
                elif line.startswith("分类:"):
                    category = line.split(":", 1)[1].strip()
                elif line.startswith("category:"):
                    category = line.split(":", 1)[1].strip()
                elif line.startswith("标签:"):
                    tags = line.split(":", 1)[1].strip()
                elif line.startswith("tags:"):
                    tags = line.split(":", 1)[1].strip()

            if not title:
                title = f"{keyword} - 深度解析" if SITE_LANGUAGE.startswith("zh") else f"Deep Dive into {keyword}"

            # 构建完整的文章文件
            return f"""---
layout: post
title: "{title}"
date: {date_str} {publish_date.strftime("%H:%M:%S")} +0800
description: "{description}"
category: "{category}"
tags: {tags}
---

{body}
"""

    # 如果格式不对，手动构建
    title = f"{keyword} - 深度解析" if SITE_LANGUAGE.startswith("zh") else f"Deep Dive into {keyword}"
    return f"""---
layout: post
title: "{title}"
date: {date_str} {publish_date.strftime("%H:%M:%S")} +0800
description: "关于{keyword}的深入分析和实用指南" if SITE_LANGUAGE.startswith("zh") else "In-depth analysis of {keyword}"
category: "默认分类"
tags: {keyword}
---

{content}
"""


def get_filename(title, publish_date):
    """生成文件名：日期-标题.md"""
    date_str = publish_date.strftime("%Y-%m-%d")
    # 简化标题作为slug
    slug = title.lower().strip()
    # 只保留字母、数字、中文字符和短横
    slug = "".join(c if c.isalnum() or c in "-一-龥" else "-" for c in slug)
    slug = slug[:50].strip("-")
    if not slug:
        slug = hashlib.md5(title.encode()).hexdigest()[:8]
    return f"{date_str}-{slug}.md"


def main():
    """主函数：每天运行一次，生成文章"""
    # 确保 _posts 目录存在
    posts_dir = Path(POSTS_DIR)
    posts_dir.mkdir(parents=True, exist_ok=True)

    # 获取关键词
    keywords = get_keywords()
    print(f"共有 {len(keywords)} 个可选话题")

    # 随机选择一个话题（每天一篇）
    keyword = random.choice(keywords)
    print(f"本日选题: {keyword}")

    # 使用今天的日期
    today = datetime.now()
    publish_date = today

    # 检查今天是否已经发布过文章
    date_prefix = today.strftime("%Y-%m-%d")
    existing_posts = list(posts_dir.glob(f"{date_prefix}-*.md"))
    if existing_posts:
        print(f"今天已经发布过文章: {existing_posts[0].name}")
        print("跳过本次生成")
        return

    # 生成文章
    raw_content = generate_article(keyword, publish_date)
    if not raw_content:
        print("文章生成失败！")
        return

    # 解析并格式化
    article = parse_article_output(raw_content, keyword, publish_date)

    # 提取标题用于文件名
    title_line = [l for l in article.split("\n") if l.startswith("title:")]
    title = title_line[0].split(":", 1)[1].strip().strip('"') if title_line else keyword

    # 生成文件名
    filename = get_filename(title, publish_date)
    filepath = posts_dir / filename

    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(article)

    print(f"文章已生成: {filepath}")
    print(f"标题: {title}")
    print("内容生成完成！")


if __name__ == "__main__":
    main()
