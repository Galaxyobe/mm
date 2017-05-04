# mm

## 介绍

mm是基于scrapy和reids实现的分布式爬虫

## 项目文件结构

    ├── company
    │   ├── airasia
    │   │   ├── fare
    │   │   │   ├── doc
    │   │   │   ├── download
    │   │   │   │   └── fare
    │   │   │   ├── fare
    │   │   │   │   └── spiders
    │   │   │   └── log
    │   │   ├── log
    │   │   └── search
    │   │       ├── doc
    │   │       └── search
    │   │           └── spiders
    │   └── lib
    │       ├── airasia
    │       ├── backends
    │       └── utils
    ├── lib
    │   └── scrapy2
    │       ├── core
    │       ├── downloadermiddlewares
    │       ├── dupefilters
    │       ├── extensions
    │       ├── pipelines
    │       ├── spiders
    │       └── utils
    └── proxy
        └── proxy
            ├── commands
            ├── rules
            └── spiders

### lib

    │── scrapy2         Scrapy框架相关的库文件

#### company

    ├── company         公司爬虫相关的文件
    │   ├── airasia     亚洲航空官网数据的爬取实例
    │   └── lib         公司爬虫相关的库文件

#### company/lib

    ├── company
    │   └── lib
    │       ├── airasia     亚洲航空数据的相关解析类
    │       ├── backends    爬取数据的存储后端
    │       └── utils       工具类

### company/airasia

    ├── company
    │   ├── airasia                 亚洲航空官网数据的爬取实例
    │   │   ├── fare                实现亚洲航空官网的价格抓取
    │   │   │   ├── doc
    │   │   │   ├── download
    │   │   │   │   └── fare
    │   │   │   ├── fare
    │   │   │   │   └── spiders
    │   │   │   └── log
    │   │   ├── log
    │   │   └── search              实现亚洲航空官网的航班信息抓取


### upload

rsync  --exclude-from='mm/.gitignore' -rR mm root@119.23.129.43:~
