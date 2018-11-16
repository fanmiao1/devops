运维系统

版本：
    Python: 3.6.1
    Django: 2.0.1

数据库(MySQL)：
    数据库名：aukey_ops
    aukey_ops.sql

    User: aukey_ops
    Password: Ops@AukeyIT$*
    

依赖包：
    requirements.txt
	

登录：
	user: aukeys
	passwd: aukeys
	
	可在/admin添加用户


修改Django包代码:

[修改用户输出显示]

在auth/models.py文件下User类下面添加：
def __str__(self):
    return self.last_name + self.first_name + '<' + self.username + '>'
