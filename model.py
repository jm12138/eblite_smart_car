import numpy as np
import paddlemobile as pm
import paddlelite as lite

'''
API 快速指南
model = pm_model(data_shape, model_dir=model_dir) -- PaddleMobile加载模型参数非合并模型
model = pm_model(data_shape, model_flie=model_flie, param_file=param_file) -- PaddleMobile加载模型参数合并模型
model = cxx_model(data_shape, model_dir=model_dir) --CxxCongig加载模型参数非合并模型
model = cxx_model(data_shape, model_flie=model_flie, param_file=param_file) -- CxxCongig加载模型参数合并模型
model.predict(inputs_data) -- 模型预测
'''

__all__ = ['cxx_model', 'pm_model']

class base_model():
	def __init__(self, data_shape, thread_num=1, model_dir=None, model_flie=None, param_file=None):
		'''
		加载模型 初始化输入张量
		参数：数据形状、线程数（Cxx_model设置无效）、（模型目录）或（模型文件、模型参数文件）
		返回：无
		'''
		self.predictor = self.load_model(model_flie, param_file, thread_num, model_dir)
		self.tensor = self.data_feed(data_shape)

class cxx_model(base_model):
	def load_model(self, model_flie, param_file, thread_num, model_dir):
		'''
		加载CxxCongig模型
		参数：模型文件、模型参数文件、线程数、模型目录
		返回：模型预测器
		'''
		valid_places =   (
			lite.Place(lite.TargetType.kFPGA, lite.PrecisionType.kFP16, lite.DataLayoutType.kNHWC),
			lite.Place(lite.TargetType.kHost, lite.PrecisionType.kFloat),
			lite.Place(lite.TargetType.kARM, lite.PrecisionType.kFloat)
		)
		config = lite.CxxConfig()
		if model_dir:
			config.set_model_dir(model_dir)
		else:
			config.set_model_file(model_flie)
			config.set_param_file(param_file)
		config.set_valid_places(valid_places)
		predictor = lite.CreatePaddlePredictor(config)
		return predictor

	def data_feed(self, data_shape):
		'''
		初始化CxxCongig模型输入数据张量
		参数：数据形状, 预测器
		返回：数据张量
		'''
		tensor = self.predictor.get_input(0)
		tensor.resize(data_shape)
		return tensor

	def predict(self, input_data):
		'''
		CxxCongig模型预测
		参数：输入数据张量、图像数据、预测器
		返回：模型预测结果
		'''
		self.tensor.set_data(input_data)
		self.predictor.run()
		out = self.predictor.get_output(0)
		result = out.data()
		return result

class pm_model(base_model):
	def load_model(self, model_flie, param_file, thread_num, model_dir):
		'''
		加载PaddleMobile模型
		参数：模型文件、模型参数文件、线程数、模型目录
		返回：模型预测器
		'''
		pm_config = pm.PaddleMobileConfig()
		pm_config.precision = pm.PaddleMobileConfig.Precision.FP32######ok
		pm_config.device = pm.PaddleMobileConfig.Device.kFPGA######ok
		if model_dir:
			pm_config.model_dir = model_dir
		else:
			pm_config.prog_file = model_flie
			pm_config.param_file = param_file
		pm_config.thread_num = thread_num    
		predictor = pm.CreatePaddlePredictor(pm_config)
		return predictor

	def data_feed(self, data_shape):
		'''
		初始化PaddleMobile模型输入数据张量
		参数：数据形状
		返回：数据张量
		'''
		tensor = pm.PaddleTensor()
		tensor.dtype =pm.PaddleDType.FLOAT32
		tensor.shape  = (data_shape)
		return tensor

	def predict(self, input_data):
		'''
		PaddleMobile模型预测
		参数：输入数据张量、图像数据、预测器
		返回：模型预测结果
		'''
		self.tensor.data = pm.PaddleBuf(input_data)
		paddle_data_feeds = [self.tensor]
		outputs = self.predictor.Run(paddle_data_feeds)
		result = np.array(outputs[0])
		return result
