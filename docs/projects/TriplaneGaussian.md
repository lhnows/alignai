代码要求19G以上显存
源码地址
https://github.com/VAST-AI-Research/TriplaneGaussian?tab=readme-ov-file
配置流程
需要挂代理，很多库模型需要vpn才能下载
torch3d安装教程 https://blog.csdn.net/qq_43426908/article/details/147427106
我的配置
我的配置采用nvidia docker 进行配置，便于打包环境进行分发在其他机器运行。
1. 下载基础镜像
docker pull nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.042. 启动镜像按照上面配置流程进行配置
启动容器命令
sudo docker run --gpus all   --shm-size=8g  -it -v ./:/app -p 7860:7860 nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04 /bin/bash注：-v 进行文件目录映射，将当前代码目录映射到服务器/app下
3. 按照配置流程配置环境
4. 下载SAM分割模型，用于去除背景
5. 运行程序
python infer.py --config config.yaml data.image_list=[example_images/a_pikachu_with_smily_face.webp,] --image_preprocess重建自己的图片只需要将上述命令中图像换为自己的图像即可
打包好的镜像直接运行
在有nvidia docker的机器上 直接运行以下命令
sudo docker run --gpus all   --shm-size=8g  -it -v ./:/app -p 7860:7860 triplanegaussian:latest /bin/bash运行demo命令 
python infer.py --config config.yaml data.image_list=[example_images/a_pikachu_with_smily_face.webp,] --image_preprocess示例输入：
示例输出
