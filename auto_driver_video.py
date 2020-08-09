# 自动行车程序（录制行车视频版）

import cv2, time

from model import pm_model
from devices import car_devices
from tool import draw_bbox, get_angle, load_label_list
from preprocess import preprocess_det, preprocess_car_line

if __name__ == "__main__":

    # 初始化变量
    Cross_Flag = 0
    limit_Flag = 0
    base_speed = 1530
    color = (255, 225, 225)
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 初始化设备
    car = car_devices()

    # 加载模型
    ssd_lite = pm_model(data_shape=(1, 3, 128, 128), model_flie='./ssd_lite/model', param_file='./ssd_lite/params')
    car_line = pm_model(data_shape=(1, 1, 128, 128), model_flie='./car_line/model', param_file='./car_line/params')

    # 加载标签列表
    label_list = load_label_list('./ssd_lite/label_list.txt')

    # 初始化视频写入器
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    videoWriter = cv2.VideoWriter('video.avi', fourcc, 25, (160, 120))
    
    # 启动前预热
    for _ in range(30):
        frame = car.read_frame()
        tmp = preprocess_det(frame, (128, 128))
        tmp = ssd_lite.predict(tmp)
        tmp = preprocess_car_line(frame, (128, 128))
        tmp = car_line.predict(tmp)
    del frame, tmp
    
    # 车辆启动
    car.lib.send_cmd(base_speed, 1500)
    
    # 主程序
    while True:
        starttime = time.time()

        # 模型预测
        frame = car.read_frame()
        img = preprocess_det(frame, (128, 128))
        result_det = ssd_lite.predict(img)
        img = preprocess_car_line(frame, (128, 128))
        result_car_line = car_line.predict(img)
        
        # 预测结果后处理
        angle = get_angle(result_car_line)
        frame, results_list = draw_bbox(result_det, frame, label_list, draw_threshold=0.7, frame_shape=None)
	
	# 若仅测试检测模型时，请将angle设置为1500，保持直行
	# angle = 1500
	
        # 前方检测到限速标志的操作
        if 'limit_10' in results_list:
            if results_list['limit_10'][1] > 40:
                if limit_Flag==0:
                    limit_Flag = 1
                    base_speed = 1525
				
        # 前方检测到解除限速标志的操作
        if 'unlimit_10' in results_list:
            if results_list['unlimit_10'][1] > 40:
                if limit_Flag==1:
                    limit_Flag = 0
                    base_speed = 1530
                    
        # 设定速度
        speed = base_speed

        # 前方检测到红灯的操作
        if 'red' in results_list:
            if results_list['red'][1] > 40:
                if Cross_Flag==0:
                    wait_start = time.time()
                    Cross_Flag = 1
        if Cross_Flag == 1:
            wait_end = time.time()
            wait_time = wait_end - wait_start
            if wait_time<=2.5:
                speed = 1500
                angle = 1500
            elif wait_time<=5.0:
                speed = base_speed
            else:
                Cross_Flag = 0
                speed = base_speed
                
        # 计算FPS
        endtime = time.time()
        fps = int(1/(endtime-starttime))
        frame = cv2.putText(frame, 'FPS:%d' % fps, (5, 12), font, 0.4, color, 1)

        # 写入视频帧
        videoWriter.write(frame)

        # 前方检测到停车场标志的操作
        if 'P' in results_list:
            if results_list['P'][1] > 60:
                car.lib.send_cmd(1500, 1500)
                break

        # 发送行车数据
        car.lib.send_cmd(speed, angle)

    # 运行结束，多生成两秒视频        
    for _ in range(48):
        starttime = time.time()
        frame = car.read_frame()
        img = preprocess_det(frame, (128, 128))
        result_det = ssd_lite.predict(img)
        frame, results_list = draw_bbox(result_det, frame, label_list, draw_threshold=0.7, frame_shape=None)
        endtime = time.time()
        fps = int(1/(endtime-starttime))
        frame = cv2.putText(frame, 'FPS:%d' % fps, (5, 12), font, 0.4, color, 1)
        videoWriter.write(frame)

    # 合成视频
    videoWriter.release()
