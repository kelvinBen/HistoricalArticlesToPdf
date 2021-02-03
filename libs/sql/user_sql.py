# -*- coding: utf-8 -*-
# Author: kelvinBen
# Github: https://github.com/kelvinBen/HistoricalArticlesToPdf

import libs.core as Core

def insert_user_info(uname,upass,token,cookie,flag):
    sql = "SELECT ui.'id' from user_info AS ui WHERE ui.'flag' = ?"
    param = (flag,)
    user_info = Core.dbpool.getOne(sql,param)
    if not user_info:   
        sql = "INSERT INTO user_info(uname,upass,token,cookie,flag) VALUES (?,?,?,?,?);"
        param = (uname,upass,token,cookie,flag)
        return Core.dbpool.insert(sql,param)
    else:
        sql = "UPDATE user_info SET 'uname'=?,'upass'=?,'token'=?,'cookie'=?,'flag'=? WHERE 'id' =?;"
        param = (uname,upass,token,cookie,flag,user_info[0])
        if not Core.dbpool.update(sql,param):
            return user_info[0]
    
def select_user_info(flag):
    sql = "SELECT ui.token,ui.cookie from user_info AS ui WHERE ui.'flag' = ?"
    param = (flag,)
    user_info = Core.dbpool.getOne(sql,param)
    return user_info
    
def delete_user_info(flag):
    sql = "DELETE FROM user_info AS ui  WHERE ui.flag = ?;"
    param = (flag,)
    user_info = Core.dbpool.delete(sql,param)
    return user_info