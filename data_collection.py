import os, cv2, time, struct, threading   
from devices import car_devices

# 初始化变量
global q, state
q = []
state = []

# 初始化设备
car = car_devices()

# 手柄遥控程序
def fn_control():
	base_speed = 1535
	while 1:
		evbuf = car.fn.read(8)
		if evbuf:
			time_fn, value, type_fn, number = struct.unpack('IhBB', evbuf)
			#print(time_fn, value, type_fn, number)
			if type_fn & 0x01:
				if number == 6:
					if value == 1 and base_speed== 1535:
						base_speed =  1525
					elif value == 1 and base_speed== 1525:
						base_speed =  1535
				if number == 1:
					if value == 1:
						data=[1500,1500]
						q.append(data)
						state.append(0)
						car.lib.send_cmd(1500,1500)
						break		
			if type_fn & 0x02:
				if number == 7:
					fvalue = value / 32767
					if fvalue == -1:
						data=[1570,1500]
						q.append(data)
						car.lib.send_cmd(1570,1500)
					elif fvalue == 1 and base_speed>1500:
						base_speed  = 1500
						data=[base_speed,1500]
						q.append(data)
						car.lib.send_cmd(base_speed,1500)
					elif fvalue == 1 and base_speed==1500:
						base_speed  = 1535
						data=[base_speed,1500]
						q.append(data)
						car.lib.send_cmd(base_speed,1500)
					else:
						data=[base_speed,1500]
						q.append(data)
						car.lib.send_cmd(base_speed, 1500)
					
				if number == 6:
					fvalue = value / 32767
					if fvalue == -1:
						data=[base_speed,1800]
						q.append(data)
						car.lib.send_cmd(base_speed, 1800)
					elif fvalue == 1:
						data=[base_speed,1200]
						q.append(data)
						car.lib.send_cmd(base_speed, 1200)
					else:
						data=[base_speed,1500]
						q.append(data)
						car.lib.send_cmd(base_speed, 1500)

# 数据保存程序			
def save_data():
	count = 0
	if not os.path.exists('./data'):
		os.mkdir('./data')	
	if not os.path.exists('./data/data'):
		os.mkdir('./data/data')
	if not os.path.exists('./data/data/img'):
		os.mkdir('./data/data/img')
	f = open('./data/data/data.txt', 'w', encoding='UTF-8')
	while 1:
		if len(q)>0:
			img = car.read_frame()
			print(q[-1],state)
			cv2.imwrite('./data/data/img/%08d.jpg' % count, img)
			count += 1
			f.write('%d\t%d\n' % (q[-1][0], q[-1][1]))
		if len(state)>0:
			f.close()
			break

# 创建两个线程
t1 = threading.Thread(target=fn_control)
t2 = threading.Thread(target=save_data)

# 等待启动指令
car.wait2start()

# 预热
for _ in range(100):
	img = car.read_frame()

# 启动线程	
t1.start()
t2.start()

# 重命名数据文件夹
t1.join()
t2.join()
os.rename('./data/data', './data/data%d' % time.time())