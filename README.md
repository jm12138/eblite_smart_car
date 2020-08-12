# eblite_smart_car
The edgeboard lite code on python api for the smart car.

# 目录结构
## 库
model.py -- 模型加载（基本无需修改）

devices.py -- 智能车设备（基本无需修改）

tool.py -- 一些工具（请根据需求自行修改）

preprocess.py -- 数据预处理（请根据模型自行修改）
## Demo（仅供参考）
auto_driver(_video).py -- 自动行车程序(行车视频)

auto_tracking(_video).py -- 原地追踪程序(行车视频)

data_collection.py -- 遥控数据采集程序(Demo版)
## 模型（车道线模型效果不好，仅供测试）
ssd_lite -- 检测模型（ssd_lite）

car_line -- 车道线模型

# API
## model
* model = pm_model(data_shape, model_dir=model_dir) -- PaddleMobile加载模型参数非合并模型
* model = pm_model(data_shape, model_flie=model_flie, param_file=param_file) -- PaddleMobile加载模型参数合并模型
* model = cxx_model(data_shape, model_dir=model_dir) -- CxxCongig加载模型参数非合并模型
* model = cxx_model(data_shape, model_flie=model_flie, param_file=param_file) -- CxxCongig加载模型参数合并模型
* model.predict(inputs_data) -- 模型预测

## devices
* car = car_devices(video_w=160, video_h=120, buffer_size=20) -- 初始化车辆设备
* car.fn -- 手柄数据流
* car.lib.send(speed, angle) -- 发送底盘操作指令
* car.read_frame() -- 读取摄像头的当前帧
* car.wait2start() -- 等待手柄发送启动指令

所有API均在代码中有详细的使用注释，方便调用和二次修改使用

# 使用提示
* 使用前请先将本项目代码clone或者下载Zip到本地，解压并将代码拷贝到智能车EdgeBoard中
* 使用自己训练的SSD_lite模型的话，请将其拷贝至ssd_lite文件夹中，重命名成model/params替换原有模型，或者修改代码中加载模型的代码

# 快速使用
```python
# python命令行快速使用
# 导入需要的包
from model import pm_model
from devices import car_devices
from preprocess import preprocess_det

# 初始化小车设备
# 可降低摄像头图像分辨率来提升运行帧率
# 可提高摄像头缓冲区大小来提升运行帧率
# 调节缓冲区大小时请注意，可能会导致摄像头前buffer_size张图片出现异常，所以最好先进行预热操作，将这些异常图片推出队列
# Baseline设置为car_devices(video_w=320, video_h=240, buffer_size=1)
car = car_devices(video_w=160, video_h=120, buffer_size=20)

# 加载模型
# 检测模型只能使用pm_model来加载
# 车道线模型可使用pm_model或者cxx_model加载
# 但若使用cxx_model加载模型，请注意提前预热模型
ssd_lite = pm_model(data_shape=(1, 3, 128, 128), model_flie='./ssd_lite/model', param_file='./ssd_lite/params')

# 读取小车摄像头图像
frame = car.read_frame()

# 预处理数据
img = preprocess_det(frame, (128, 128))

# 模型预测
result = ssd_lite.predict(img)

# 打印结果
print(result)
```
# Demo使用
```shell
# shell
# 运行前请先阅读一下程序的代码

# 数据采集
python data_collection.py

# 自动行车
python auto_driver.py

# 原地追踪
python auto_driver.py
```
# 如何部署自己的模型
1. 使用paddlepaddle训练自己的模型

2. 导出推理模型

3. 拷贝推理模型到智能车Edgeboard上

3. 使用model模块中pm_model或cxx_model这两个api加载刚刚拷贝的模型

4. 根据自己的模型写好数据的预处理代码

5. 调用model类的predict函数进行预测

6. 编写预测后的后续操作
