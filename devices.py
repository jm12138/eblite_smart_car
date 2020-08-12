import cv2, select, struct, v4l2capture
import numpy as np

from ctypes import cdll

__all__ = ['car_devices']

class car_devices():
	def __init__(
                self, video_device='/dev/video2', fn='/dev/input/js0', 
                lib_path='/home/root/workspace/deepcar/deeplearning_python/lib/libart_driver.so', 
                ttyUSB='/dev/ttyUSB0', video_w=160, video_h=120, buffer_size=20
                ):
		'''
		初始化车辆设备
		参数：视频设备、手柄设备、底盘lib路径、ttyUSB设备、摄像头图像宽度、摄像头图像高度、视频流缓冲值
		返回：无
		'''
		self.video = self.video_cap(video_device, video_w, video_h, buffer_size)
		self.fn = self.config_fn(fn)
		self.lib = self.load_lib(lib_path, ttyUSB)

	def video_cap(self, video_device, video_w, video_h, buffer_size):
		'''
		启动摄像头录像
		参数：设备路径
		返回：视频流
		'''
		video = v4l2capture.Video_device(video_device)
		video.set_format(video_w, video_h, fourcc='MJPG')
		video.create_buffers(buffer_size)
		video.queue_all_buffers()
		video.start() 
		return video
		
	def config_fn(self, fn):
		'''	
		读取手柄数据
		参数：设备路径
		返回：手柄数据流
		'''
		fn = open(fn, 'rb')
		return fn

	def load_lib(self, lib_path, ttyUSB):
		'''
		加载底盘驱动程序
		参数：lib路径
		返回：lib调用端口
		'''
		lib = cdll.LoadLibrary(lib_path)
		lib.art_racecar_init(38400, ttyUSB.encode("utf-8"))
		return lib

	def wait2start(self):
		'''
		等待启动指令（通过单击手柄左侧的向上按键启动）
		参数：无
		返回：无
		'''
		print('Wait to start!\nPlease press the top button to start the program.')
		while 1:
			evbuf = self.fn.read(8)
			if evbuf:
				time_fn, value, type_fn, number = struct.unpack('IhBB', evbuf)
				if type_fn & 0x02:
					if number == 7:
						fvalue = value / 32767
						if fvalue == -1:
							break
	
	def read_frame(self):
		'''
		读取当前视频帧
		参数：无
		返回：当前帧图像
		'''
		select.select((self.video,), (), ())
		image_data = self.video.read_and_queue()
		frame = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
		return frame
