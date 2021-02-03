# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/HistoricalArticlesToPdf

import libs.core as Core

def insert_info(fakeid,alias,nickname):
    sql = ("SELECT wi.id FROM wechat_info  AS wi WHERE wi.nickname = ?; ")
    param = (nickname,)
    wechat_info =  Core.dbpool.getOne(sql,param)
    if not wechat_info:
        sql = ("INSERT INTO wechat_info('fakeid', 'alias', 'nickname') VALUES (?,?,?);")
        param = (fakeid,alias,nickname)
        return Core.dbpool.insert(sql,param)
    else:
        sql = ("UPDATE wechat_info SET 'fakeid'=?,'alias'=?,'nickname'=? WHERE 'id'=?;") 
        param = (fakeid,alias,nickname,wechat_info[0])
        if not Core.dbpool.update(sql,param):
            return wechat_info[0]

def insert_list(wi_id,num,title,link,digest,i_date):
    sql =  ("SELECT wl.'id' FROM wechat_list AS wl WHERE wl.'wi_id' = ? and wl.'title'=?;")
    param = (wi_id,title)
    wechat_list = Core.dbpool.getOne(sql,param)
    if not wechat_list:
        sql = ("INSERT INTO wechat_list('wi_id', 'title', 'link','digest','num','add_time','update_time') VALUES (?,?,?,?,?,?,?);")
        param = (wi_id,title,link,digest,num,i_date,i_date)
        return Core.dbpool.insert(sql,param)
    else:
        sql = ("UPDATE wechat_list SET 'wi_id'=?,'title'=?,'link'=?,'digest'=?,'num'=?,'update_time'=? WHERE 'id' =?;")
        param = (wi_id,title,link,digest,num,i_date,wechat_list[0])
        if not Core.dbpool.update(sql,param):
            return wechat_list[0]

def select_list_num(wi_id):
    sql =  ("SELECT wl.'num' FROM wechat_list AS wl WHERE wl.'wi_id' = ? ORDER BY wl.'num' DESC;")
    param = (wi_id,)
    wechat_list = Core.dbpool.getOne(sql,param)
    if not wechat_list:
        return 1
    num = int(wechat_list[0])
    nums = str(num/10).split(".")
    if int(nums[1]) >= 5:
        start = num - int(nums[1]) + 5
    else:
        start = num - int(nums[1]) 
    return start

def select_list_title(wi_id,start):
    sql =  "SELECT wl.'title',wl.'num' FROM wechat_list AS wl WHERE wl.'wi_id' = ? ORDER BY wl.'num' DESC LIMIT 5 OFFSET ? ;"
    param = (wi_id,start)
    return Core.dbpool.getAll(sql,param)

def select_list_to_diz(wi_id,i_date):
    sql =  ("SELECT wl.'title' FROM wechat_list AS wl WHERE wl.'wi_id' = ? and wl.'update_time' >= ?;")
    param = (wi_id,i_date)
    wechat_list = Core.dbpool.getAll(sql,param)
    return wechat_list
