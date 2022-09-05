---
template: main
---

# {{ site.config.name }} ({{ site.config.email }})

| Company | Year range |
| ------- | ---------- |
{%- for company in site.data.companies %}
| {{ company.name }} | {{ company.year_range }} |
{%- endfor %}
