import pymysql
import json
import datetime
f = open("sql.conf","r")
data = json.loads(f.read())
USR = data['username']
PAS = data['password']
HOST = data['host']
cx = pymysql.connect(user=USR, password=PAS,database='bob_live_sa',host=HOST)
cu = cx.cursor()
max_date = datetime.datetime.now() + datetime.timedelta(days = 5)
max_date = max_date.strftime('%Y-%m-%d')
q = "SELECT `code` FROM `sales_rule` WHERE `is_active` = 1 AND date(`to_date`) LIKE '2015-05-31'"
print q
cu.execute(q)
coupons = []
for x in cu:
	coupons.append(x[0])
#print coupons
cu.close()
cx.close()
cx = pymysql.connect(user='referaly', password='CCTx2aNE8DB',database='referaly',host='167.114.109.33')
cu = cx.cursor()
c_list = "','".join(coupons)
etl_q = "SELECT users.time,users.email,wadi_v1_coupons.coupon,wadi_v1_coupons.type FROM `users`,`wadi_v1_coupons` where users.id=wadi_v1_coupons.uid AND SUBSTRING(wadi_v1_coupons.coupon, 1, CHAR_LENGTH(wadi_v1_coupons.coupon) - 2) IN ('%s') order by users.id LIMIT 5"%(c_list)

#print etl_q
cu.execute(etl_q)
for x in cu:
	print x
