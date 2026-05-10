---
layout: home
title: 首页
---

# AI产品观察

**聚焦AI时代的产品思维、工具评测与行业洞察**

欢迎来到 AI产品观察！我们每日更新关于AI工具、产品管理、电商趋势的深度内容。所有文章均由AI辅助生成，结合行业专家的经验，为你提供最新鲜、最实用的内容。

## 热门分类

- [AI工具评测]({{ '/category/ai-tools/' | relative_url }}) — 最新AI产品实战测评
- [产品管理]({{ '/category/product/' | relative_url }}) — PM技能提升指南
- [电商运营]({{ '/category/ecommerce/' | relative_url }}) — 电商趋势与运营策略
- [行业洞察]({{ '/category/insights/' | relative_url }}) — 深度行业分析

## 最新文章

{% for post in site.posts limit:5 %}
- [{{ post.title }}]({{ post.url }}) — {{ post.date | date: "%Y-%m-%d" }}
{% endfor %}

---

{% if paginator.total_pages > 1 %}
<div class="pagination">
  {% if paginator.previous_page %}
    <a href="{{ paginator.previous_page_path | relative_url }}">&laquo; 上一页</a>
  {% endif %}
  {% for page in (1..paginator.total_pages) %}
    {% if page == paginator.page %}
      <em>{{ page }}</em>
    {% elsif page == 1 %}
      <a href="{{ '/' | relative_url }}">{{ page }}</a>
    {% else %}
      <a href="{{ site.paginate_path | relative_url | replace: ':num', page }}">{{ page }}</a>
    {% endif %}
  {% endfor %}
  {% if paginator.next_page %}
    <a href="{{ paginator.next_page_path | relative_url }}">下一页 &raquo;</a>
  {% endif %}
</div>
{% endif %}
