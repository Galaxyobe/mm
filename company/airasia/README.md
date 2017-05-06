# AirAsia

## Spiders

* search

## Install

### Ubuntu 16.04

### install redis

> sudo apt-get install redis-server redis-tools

#### install pip

> sudo apt-get install python-pip

#### install requirements or install in system lib

> pip install -r requirements.txt

or 

> sudo pip install -r requirements.txt

## Usage

### generator url into the redis

> $ python start.py

### start crawl in search dir

> $ scrapy crawl search

### start crawl in fare dir

> $ scrapy crawl fare


## 常用命令

### 生成url
> ./spider.py gen -s airasia airasia -d CAN -a DEL -D 10 --set-redis host=127.0.0.1 port=6379 db=0 password=datacenter.io

### 监控运行结果 
> ./spider.py mon --set-redis host=127.0.0.1 port=6379 db=1 password=datacenter.io -d

### 运行
> ./spider.py run -n fare -l './log' -D