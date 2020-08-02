# 自动追踪标识程序

import cv2, time

from model import pm_model
from devices import car_devices
from tool import draw_bbox, load_label_list
from preprocess import preprocess_det

if __name__ == "__main__":

    # 初始化变量
    count = 0
    color = (255, 225, 225)
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # 初始化设备
    car = car_devices()

    # 加载模型
    ssd_lite = pm_model(data_shape=(1, 3, 128, 128), model_flie='./ssd_lite/model', param_file='./ssd_lite/params')

    # 加载标签列表
    label_list = load_label_list('./ssd_lite/label_list.txt')

    # 初始化视频写入器
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    videoWriter = cv2.VideoWriter('video.avi', fourcc, 25, (160, 120))

    # 等待启动指令
    car.wait2start()

    # 启动前预热
    for _ in range(30):
        frame = car.read_frame()
        tmp = preprocess_det(frame, (128, 128))
        tmp = ssd_lite.predict(tmp)
    del frame, tmp

    # 主程序
    while count<500:
        starttime = time.time()
    
        # 初始化状态
        state = 'stop'
        count += 1
        
        # 模型预测
        frame = car.read_frame()
        img = preprocess_det(frame, (128, 128))
        result_det = ssd_lite.predict(img)
        
        # 预测结果后处理
        frame, results_list = draw_bbox(result_det, frame, label_list, draw_threshold=0.7, frame_shape=None)

        # 追踪限速标志
        if 'limit_10' in results_list:
            dx = results_list['limit_10'][0]-80
            if abs(dx)>25:
                if dx>0:
                    state = 'right'
                else:
                    state = 'left'

        # 发送转动信息
        if state=='right':
            car.lib.send_cmd(1530,500)
        elif state=='left':
            car.lib.send_cmd(1530,2500)
        else:
            car.lib.send_cmd(1500,1500)           
             
        # 计算FPS
        endtime = time.time()
        fps = int(1/(endtime-starttime))
        frame = cv2.putText(frame, 'FPS:%d' % fps, (5, 12), font, 0.4, color, 1)

        # 写入视频帧
        videoWriter.write(frame)
        
    # 停车        
    car.lib.send_cmd(1500,1500)
        
    # 合成视频
    videoWriter.release()