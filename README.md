# HistoricalArticlesToPdf
一款可以将任意微信历史文章、知识星球历史文章、博客文章批量转换为PDF的工具。

### 功能列表

#### 已完善的功能
- 多公众号文章提取
- 任意微信公众号文章提取
- 生成PDF文件以及HTML文件
- 对文章中的图片自动下载
- 增量获取公众号文章
- 多线程对文章进行转换

#### 计划中的功能
- 使用微信账号进行公众号的提取
- 使用cookie对公众号的提取
- 知识星球历史文章的提权
- 博客文章的提取
- 红队相关情报信息提取
- 对论坛权重文章进行爬取

### 必读

> PS: 本项目依赖三方软件 wkhtmltopdf, 使用前需要先行安装wkhtmltopdf。

wkhtmltopdf的下载地址:
```
官网下载页面: https://wkhtmltopdf.org/downloads.html
```

### 使用方法

#### 1. 下载代码到本地
```
git clone https://github.com/kelvinBen/HistoricalArticlesToPdf.git
```

#### 2. 进入代码目录
```
cd HistoricalArticlesToPdf
```

#### 3.安装依赖库
```
python3 -m  pip install -r requirements.txt
```

#### 4.运行

提取一个公众号文章信息
```
python3 app.py wechat -n 公众号名称 -o pdf以及html文件输出目录
```

提取多个公众号文章信息

```
python3 app.py wechat -n 公众号名称1、公众号名称2、公众号名称3 -o pdf以及html文件输出目录
```
