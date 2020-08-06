#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/HistoricalArticlesToPdf

import click
import logging
from libs.core import Bootstrapper
from libs.task.wechat_task import WechatTask

log = logging.getLogger(__name__)

@click.group(help="")
def cli():
    pass

# 微信公众号/微信
@cli.command(help="Convert historical articles of WeChat public account to pdf.")
@click.option("-u","--user-name",required=False,type=str,help="Use the username or password to log in to the WeChat official account and obtain historical articles on the WeChat official account.")
@click.option("-p","--password",required=False,type=str,help="Use the username or password to log in to the WeChat official account and obtain historical articles on the WeChat official account.")
@click.option("-c","--cookie",required=False,type=str,help="Get historical articles of WeChat official account through cookies。")
@click.option("-w","--website-url",required=False,type=str,help="Convert the URL address of the specified historical article to pdf.")
@click.option("-t","--threads",required=False,type=int,default=10,help="Set the number of threads to generate PDF files.")
@click.option("-o","--out-path",required=True,type=str,help="Set the output directory of the PDF file.")
@click.option("-n","--name",required=True,type=str,help="Specify the name of the WeChat official account. For multiple WeChat official accounts, please use ',' to split.")
def wechat(user_name: str, password: str, cookie: str, name: str, website_url: str, threads:str, out_path:str) -> None:
    try:
        # 初始化全局对象
        bootstrapper = Bootstrapper(__file__,out_path)
        bootstrapper.init()
        
        task = WechatTask(user_name, password, cookie,name,website_url,threads,out_path)
        task.start()
    except Exception as e:
        raise e
        log.error(e)


# web网站
def website():
    pass

# 知识星球
def zsxq():
    pass


def main():
    cli()


if __name__ == "__main__":
    main()