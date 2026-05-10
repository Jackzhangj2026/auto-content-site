---
layout: page
title: 归档
permalink: /archives/
---

## 文章归档

{% assign posts_by_year = site.posts | group_by_exp: "post", "post.date | date: '%Y'" %}

{% for year in posts_by_year %}
### {{ year.name }} ({{ year.items | size }} 篇)

{% for post in year.items %}
- **{{ post.date | date: "%m-%d" }}** — [{{ post.title }}]({{ post.url | relative_url }}){% endfor %}

{% endfor %}
