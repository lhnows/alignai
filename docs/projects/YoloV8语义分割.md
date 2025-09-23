完整的YOLOv8图像语义分割教程，从最开始的 **数据标注** 一步步到最终的 **模型训练和预测**。

### **教程大纲**

1. **环境准备**：安装必要的软件和库。  
2. **数据标注**：使用LabelMe工具为你的图像创建多边形掩码。  
3. **格式转换**：将LabelMe的JSON格式转换为YOLOv8所需的TXT格式。  
4. **创建数据集配置文件**：编写.yaml文件，告诉YOLOv8如何加载你的数据。  
5. **模型训练**：使用命令行或Python脚本开始训练。  
6. **模型推理和可视化**：使用你训练好的模型进行预测。

---

### **第1步：环境准备**

首先，确保你的环境满足要求。强烈建议使用配备NVIDIA GPU的Linux或Windows系统。

1. **创建Python虚拟环境** (推荐)  
   Bash  
   ```
   conda create -n yolov8_env python=3.10
   # 激活环境  
   # Windows:  
   conda activate yolov8_env  
   # Linux/macOS:  
   conda activate yolov8_env  
   ```
2. 安装PyTorch  
   访问 PyTorch官网，根据你的CUDA版本选择合适的命令进行安装。例如：  
   Bash  
   # 例如，使用CUDA 12.1 
   ``` 
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   ```
3. **安装YOLOv8 (ultralytics)**  
   Bash  
   ```
   pip install ultralytics
   ```
4. **安装标注工具LabelMe**  
   Bash  
   ```
   pip install labelme
   ```
---

### **第2步：数据标注**

语义分割需要为每个目标物体绘制精确的轮廓（多边形）。LabelMe 是一个非常经典和好用的工具。

1. 启动LabelMe  
   在你的终端（激活了虚拟环境）中输入：  
   ```
   labelme
   ```
2. **标注流程**  
   * **打开图片**：点击 "Open Dir"，选择你存放所有待标注图片的文件夹。  
   * **创建多边形**：点击左侧工具栏的 "Create Polygons"。  
   * **绘制轮廓**：沿着你想要分割的物体的边缘，通过点击鼠标左键来放置顶点。尽量精确地勾勒出物体的轮廓。完成一个闭合区域后，LabelMe会弹出一个对话框。  
   * **输入标签**：在弹出的对话框中输入该物体的类别名称，例如 cat, dog, car 等。  
   * **保存**：完成一张图片的所有物体标注后，点击 "Save"。LabelMe会在图片旁边生成一个同名的 .json 文件，这个文件包含了你绘制的所有多边形坐标和标签信息。

**完成后，你的文件夹应该是这样的：**

raw_data/  
├── 1.jpg  
├── 1.json  
├── 2.jpg  
├── 2.json  
└── ...

---

### **第3步：格式转换 (从 LabelMe JSON 到 YOLOv8 TXT)**

YOLOv8分割任务需要的标签格式非常特殊：每个图片对应一个 .txt 文件，文件内容如下：  
```
<class_index> <x1_norm> <y1_norm> <x2_norm> <y2_norm> ...
```
* <class_index>: 类别索引，从0开始。  
* <x_norm> <y_norm>: 物体轮廓上每个顶点的归一化坐标（值在0到1之间）。

我们需要写一个脚本来完成这个转换，并自动划分训练集和验证集。

1. 创建项目文件夹结构  
   建议组织成这样：  
   ```
   YOLOv8-Seg-Project/  
   ├── labelme_to_yolo.py   # 我们即将创建的转换脚本  
   ├── raw_data/            # 存放你用LabelMe标注好的 jpg 和 json  
   └── dataset/             # 转换后，符合YOLOv8格式的数据将存放在这里  
       ├── images/  
       │   ├── train/  
       │   └── val/  
       ├── labels/  
       │   ├── train/  
       │   └── val/
   ```
2. **编写 labelme_to_yolo.py 转换脚本**  
   Python  
```
   import os  
   import json  
   import shutil  
   from sklearn.model_selection import train_test_split  
   from tqdm import tqdm

   def convert_labelme_to_yolo(labelme_dir, output_dir, class_mapping):  
       """  
       将 LabelMe 标注的 JSON 文件转换为 YOLOv8 分割所需的 TXT 格式。

       Args:  
           labelme_dir (str): 存放 LabelMe JSON 和对应图片的文件夹路径。  
           output_dir (str): 输出YOLOv8格式数据集的根目录。  
           class_mapping (dict): 类别名称到索引的映射，例如 {'cat': 0, 'dog': 1}。  
       """  
       # 创建输出目录结构  
       os.makedirs(os.path.join(output_dir, 'images', 'train'), exist_ok=True)  
       os.makedirs(os.path.join(output_dir, 'images', 'val'), exist_ok=True)  
       os.makedirs(os.path.join(output_dir, 'labels', 'train'), exist_ok=True)  
       os.makedirs(os.path.join(output_dir, 'labels', 'val'), exist_ok=True)

       # 收集所有 json 文件  
       json_files = [f for f in os.listdir(labelme_dir) if f.endswith('.json')]

       # 划分训练集和验证集  
       train_files, val_files = train_test_split(json_files, test_size=0.2, random_state=42)

       # 处理文件  
       process_files(train_files, 'train', labelme_dir, output_dir, class_mapping)  
       process_files(val_files, 'val', labelme_dir, output_dir, class_mapping)

       print("转换完成！")

   def process_files(files, split, labelme_dir, output_dir, class_mapping):  
       """  
       处理单个数据集划分（训练或验证）。  
       """  
       print(f"正在处理 {split} 集...")  
       for json_file in tqdm(files):  
           base_name = os.path.splitext(json_file)[0]  
           json_path = os.path.join(labelme_dir, json_file)

           # 找到对应的图片文件（支持多种格式）  
           image_path = None  
           for ext in ['.jpg', '.jpeg', '.png']:  
               potential_path = os.path.join(labelme_dir, base_name + ext)  
               if os.path.exists(potential_path):  
                   image_path = potential_path  
                   break

           if not image_path:  
               print(f"警告：找不到 {json_file} 对应的图片文件，跳过。")  
               continue

           # 复制图片到目标文件夹  
           shutil.copy(image_path, os.path.join(output_dir, 'images', split, os.path.basename(image_path)))

           # 读取 JSON 文件  
           with open(json_path, 'r') as f:  
               data = json.load(f)

           img_width = data['imageWidth']  
           img_height = data['imageHeight']

           yolo_labels = []  
           for shape in data['shapes']:  
               label = shape['label']  
               if label not in class_mapping:  
                   continue

               class_id = class_mapping[label]  
               points = shape['points']

               # 归一化坐标  
               normalized_points = []  
               for x, y in points:  
                   norm_x = x / img_width  
                   norm_y = y / img_height  
                   normalized_points.extend([norm_x, norm_y])

               yolo_labels.append(f"{class_id} " + " ".join(map(str, normalized_points)))

           # 写入 YOLO 格式的 txt 文件  
           label_path = os.path.join(output_dir, 'labels', split, base_name + '.txt')  
           with open(label_path, 'w') as f:  
               f.write("n".join(yolo_labels))

   if __name__ == '__main__':  
       # --- 配置 ---  
       # 1. 定义你的类别和它们对应的索引  
       CLASS_MAPPING = {  
           'cat': 0,  
           'dog': 1,  
           # 在这里添加你自己的类别  
       }

       # 2. 指定原始数据文件夹和输出文件夹  
       RAW_DATA_DIR = './raw_data'  
       OUTPUT_DATASET_DIR = './dataset'

       # --- 运行转换 ---  
       convert_labelme_to_yolo(RAW_DATA_DIR, OUTPUT_DATASET_DIR, CLASS_MAPPING)
```
3. **运行脚本**  
   * 修改脚本中 CLASS_MAPPING，定义好你自己的类别。  
   * 确保 RAW_DATA_DIR 指向你标注好的数据文件夹。  
   * 在终端运行：python labelme_to_yolo.py  
   * 脚本运行结束后，你的 dataset 文件夹下就会生成YOLOv8所需的完整数据结构。

---

### **第4步：创建数据集配置文件 (.yaml)**

你需要创建一个 .yaml 文件来告诉YOLOv8数据集的位置、类别数量和名称。

在你的项目根目录 (YOLOv8-Seg-Project/)下创建一个文件，例如 my_dataset.yaml，内容如下：

YAML
```
# 数据集根目录的绝对路径或相对于 yolov8/ 目录的相对路径  
path: ./dataset  # 或者填写绝对路径: D:/path/to/YOLOv8-Seg-Project/dataset

# 训练集和验证集的图片路径  
train: images/train  
val: images/val

# 类别信息  
names:  
  0: cat  
  1: dog  
  # 确保这里的索引和名称与你 CLASS_MAPPING 中的一致
```
---

### **第5步：模型训练**

万事俱备，现在可以开始训练了！

* **选择预训练模型**：YOLOv8提供了一系列不同大小的分割预训练模型，如 yolov8n-seg.pt (最快), yolov8s-seg.pt, yolov8m-seg.pt 等。初次尝试建议从 n 或 s 版本开始。  
* 使用命令行训练 (最简单)  
  在你的项目根目录下打开终端（确保虚拟环境已激活），运行以下命令：  
  Bash  
  yolo segment train data=my_dataset.yaml model=yolov8s-seg.pt epochs=100 imgsz=640

  * data: 指向你刚刚创建的 .yaml 配置文件。  
  * model: 指定使用的预训练模型。  
  * epochs: 训练的总轮数。  
  * imgsz: 训练时输入的图片尺寸。

训练开始后，YOLOv8会自动下载预训练模型，并显示训练进度。训练完成后，所有结果（包括训练好的模型权重）会保存在 runs/segment/train/ 目录下。最好的模型通常是 runs/segment/train/weights/best.pt。

---

### **第6步：模型推理和可视化**

训练完成后，使用你自己的模型进行预测。

* **使用命令行预测**  
  Bash  
  ```
  yolo segment predict model=runs/segment/train/weights/best.pt source='path/to/your/test_image.jpg'
  ```
  * model: 指向你训练好的 best.pt 模型。  
  * source: 可以是单张图片、整个文件夹或视频文件。

预测结果（带分割掩码的图片）会保存在 runs/segment/predict/ 目录下。

* **使用Python脚本预测**  
  Python  
  ```
  from ultralytics import YOLO  
  import cv2

  # 加载你训练好的模型  
  model = YOLO('runs/segment/train/weights/best.pt')

  # 进行预测  
  results = model('path/to/your/test_image.jpg')

  # results[0] 包含了对第一张图片的所有检测结果  
  res_plotted = results[0].plot()

  # 显示结果  
  cv2.imshow("result", res_plotted)  
  cv2.waitKey(0)  
  cv2.destroyAllWindows()
  ```
至此，你已经完成了从数据标注到模型部署的全过程！祝你训练顺利！
