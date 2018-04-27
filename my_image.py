#!/bin/evn python
# _*_coding:utf-8 _*_
import urllib2
import urllib
import requests
import ssl
import cookielib
import json
#网站证书步验证：因为改网站没有证书，python访问时会报证书错误
ssl._create_defaulf_https_context=ssl._create_unverified_context
#建立cookie对象
cj = cookielib.Cookiejar()
cookieHandle = urllib2.HTTPCookieProcessor(cj)
新建一个触发，复用之前的cookie,模拟同一个操作（把cookie)对象绑定到opener)
opener = urllib2.build_opener(cookieHandle)

#第一步：请求获取验证码的图片
#图片的url
imgurl="https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.9254950588733393"
#图片请求的头信息
img_headers{"User-Agent":"Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36}
#建立一个请求对象
req - urllib2.Request(imgurl)
#发送get请求并返回数据
imgcode = opener.open(req).read()
with open('code.png','wb') as fn:
    fn.write(imgcode)
    
#第二步:post提交验证码
#提交验证码的url
img_post_url ="https://kyfw.12306.cn/passport/captcha/captcha-check"
#提交验证码的头部信息
#建立请求对象
req = urllib2.Request(img_post_url)
#对象添加请求信息
req.headers = img_headers
#要提交的表单数据
post_num = raw_input("请输入验证码")
data={"answer":post_num,
      "login_site":"E",
      "rand":"sirand"}
#数据转换成网站可以接受的字符串
mydata = urllib.urlencode(datra)
#发送post请求提交数据并返回数据
img_post_htnl = opener.open(req,madata),read()
#with open('img_post_html.text','wb') as fn:
#            fn.write(img_post_html)
print img_post_html
#第三步:post提交账户信息登入
#登入的url
#登入的头部信息
#建立请求对象
#对象添加头部信息
#组织要提交的表单信息
#数据格式转换
#发送post请求并返回数据
