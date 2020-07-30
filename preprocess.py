import cv2
import numpy as np

from PIL import Image

__all__ = ['preprocess_det', 'preprocess_car_line']

def preprocess_det(img, img_shape):
	'''
	检测模型输入数据预处理
	参数：未处理的图像
	返回：预处理后的图像
	'''
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	img = Image.fromarray(img)
	img = img.resize(img_shape, 1)
	img = np.array(img).astype(np.float32)
	mean = np.array([0.485, 0.456, 0.406])[np.newaxis, np.newaxis, :]
	std = np.array([0.229, 0.224, 0.225])[np.newaxis, np.newaxis, :]
	img = img / 255.0
	img -= mean
	img /= std
	img = img.transpose((2, 0, 1))
	img = np.expand_dims(img, axis=0)
	img = np.array(img).astype(np.float32)
	return img

def preprocess_car_line(img, img_shape):
	'''
	车道线模型输入数据预处理
	参数：未处理的图像
	返回：预处理后的图像
	'''
	lower_hsv = np.array([20, 75, 165])
	upper_hsv = np.array([40, 255, 255])
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, lowerb=lower_hsv, upperb=upper_hsv)
	img = Image.fromarray(mask)
	img = img.resize(img_shape, Image.ANTIALIAS)
	img = np.array(img).astype(np.float32)
	img = img / 255.0
	img = np.expand_dims(img, 0)
	img = np.expand_dims(img, 0)
	return img