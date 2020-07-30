# eblite_smart_car
The edgeboard code on python api for the smart car.

# 目录结构
## 库
model.py -- 模型加载

tool.py -- 一些工具

devices.py -- 智能车设备

preprocess.py -- 数据预处理
## Demo
auto_driver(_video).py -- 自动行车程序(行车视频)

auto_tracking(_video).py -- 原地追踪程序(行车视频)

# API
所有API均在代码中有详细的使用注释，方便调用和二次修改使用

# 快速使用
```python
# 导入需要的包
from model import model
from devices import car_devices
from preprocess import preprocess_det

# 加载模型
ssd_lite = pm_model('./ssd_lite/model', './ssd_lite/params', (1, 3, 128, 128))

# 初始化小车设备
car = car_devices()

# 读取小车摄像头图像
frame = car.read_frame()

# 预处理数据
img = preprocess_det(frame, (128, 128))

# 模型预测
result = ssd_lite.predict(img)

# 打印结果
print(result)
```
