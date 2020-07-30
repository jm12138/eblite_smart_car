# 自动行车程序

import time

from model import pm_model
from devices import car_devices
from tool import draw_bbox, load_label_list, get_angle
from preprocess import preprocess_det, preprocess_car_line

if __name__ == "__main__":

    # 初始化变量
    Cross_Flag = 0
    limit_Flag = 0
    base_speed = 1530
    
    # 初始化设备
    car = car_devices()

    # 加载模型
    ssd_lite = pm_model('./ssd_lite/model', './ssd_lite/params', (1, 3, 128, 128))
    car_line = pm_model('./car_line/model', './car_line/params', (1, 1, 128, 128))

    # 加载标签列表
    label_list = load_label_list('./ssd_lite/label_list.txt')
   
    # 等待启动指令
    car.wait2start()
    
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

        # 模型预测
        frame = car.read_frame()
        img = preprocess_det(frame, (128, 128))
        result_det = ssd_lite.predict(img)
        img = preprocess_car_line(frame, (128, 128))
        result_car_line = car_line.predict(img)
        
        # 预测结果后处理
        angle = get_angle(result_car_line)
        results_list = draw_bbox(result_det, frame=None, label_list=label_list, draw_threshold=0.7, frame_shape=[120, 160])
        
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

        # 前方检测到人行横道的操作
        if 'Cross' in results_list:
            if results_list['Cross'][1] > 40:
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
				          
        # 前方检测到停车场标志的操作
        if 'P' in results_list:
            if results_list['P'][1] > 60:
                car.lib.send_cmd(1500, 1500)
                break

        # 发送行车数据
        car.lib.send_cmd(speed, angle)