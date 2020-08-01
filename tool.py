import cv2
import numpy as np

__all__ = ['load_label_list', 'get_angle', 'draw_bbox']

def load_label_list(label_txt):
    '''
    加载标签列表
    参数：标签列表文件
    返回：标签列表
    '''
    with open(label_txt, 'r', encoding='UTF-8') as f:
        label_list = f.read()[:-1].split('\n')
    return label_list

def get_angle(reslut):
    '''
    计算角度输出值
    参数：模型预测结果
    返回：角度值
    '''
    reslut = reslut[0][0]
    if reslut>1:
        reslut = 1
    elif reslut<0:
        reslut = 0
    angle = int(reslut*600+1200)
    return angle

def draw_bbox(results, frame, label_list, draw_threshold, frame_shape):  
	'''
	绘制检测模型的预测框
	参数：模型预测结果、模型输入的预测图像、标签对应列表、绘制阈值、图像形状
	返回：预测框绘制完成的图像、预测类别结果列表（模型输入的预测图像存在时）或只返回预测类别结果列表
	'''
	results_list = {}
	font = cv2.FONT_HERSHEY_SIMPLEX
	for bbox in results:          
		if type(bbox) is not np.ndarray:
			continue
		label, score, x1, y1, x2, y2 = bbox
		if label == 0:
			continue
		if score > draw_threshold:
			if type(frame) is np.ndarray:
			    h, w = frame.shape[:2]
			else:
			    h, w = frame_shape
			x1 *= w
			x2 *= w
			y1 *= h
			y2 *= h
			x_c = (x1+x2)/2
			y_c = (y1+y2)/2
			bbox = [int(round(x)) for x in [x1, y1, x2, y2]]
			label_name = label_list[int(label)]
			if type(frame) is np.ndarray:
			    frame = cv2.putText(frame, label_name, (bbox[0], bbox[1]-2), font, 0.4, (255, 0, 0), 1)
			    frame = cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0,0,255), 1)
			results_list[label_name] = [x_c, y_c]
	if type(frame) is np.ndarray:
	    return frame, results_list
	else:
	    return results_list