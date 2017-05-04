# proxy

## 依赖

---

* Scrapy
* Scrapy_Redis
* Redis

## 介绍

---

### 抓取代理信息

* 使用Scrapy根据书写的规则[proxy/rules/rule.py]从IP代理网站抓取代理信息
* 使用xpath/css提取元素保存至Redis



## 使用

---

### 开始抓取

执行的是自定义命令:proxy/commands/proxy.py

> $ scrapy proxy


