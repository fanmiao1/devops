#import dbutil
import config
#db = dbutil.DB(config.db,config.db_host,config.db_user,config.db_passwd)

status = {}
ips = {}
for line in open('log.log'):
    tmp = line.split(' ')
    ip,code = tmp[0] ,tmp[8]
    status[code] = status.get(code,0)+1 
    ips[ip] = ips.get(ip,0)+1
print status
for k,v in status.items():
    sql = 'insert into status  (status,count) values ("%s",%d)' % (k,v)
    print sql
#print ips
for res in sorted(ips.items(),key=lambda x:-x[1])[:10]:
    print res
    sql = 'insert into top_ip  (ip,count) values ("%s",%d)'%(res[0],res[1])
    print sql
#d    db.execute(sql)
