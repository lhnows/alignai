# Teaser++ 综合指南

## TEASER++: 快速且可认证的鲁棒点云配准算法深度解析

**TEASER++** 是三维计算机视觉和机器人领域中的一个里程碑式算法，为点云配准问题提供了一个快速且极其鲁棒的解决方案。该算法由麻省理工学院（MIT）SPARK实验室的研究人员开发，旨在即使在存在极端数量的异常对应点（outlier correspondences）的情况下，也能成功对齐两个三维点云。在现实世界的应用中，处理大量的异常值是一个普遍存在的难题。而TEASER++的独特之处在于其“**可认证性**”（certifiable），即在特定条件下，它能提供数学保证，确保找到的解是全局最优解。

### 核心概念：它是什么以及解决什么问题

TEASER++ 的核心是解决**刚性点云配准**（rigid point cloud registration）问题。这指的是寻找一个最优的刚性变换（即旋转和平移），以将一个“源”点云与一个“目标”点云对齐。这是一项基础性任务，广泛应用于以下领域：

- **同步定位与建图 (SLAM):** 用于闭环检测和地图构建。
- **三维重建:** 将物体或环境的多次扫描融合成一个完整的模型。
- **物体识别与位姿估计:** 确定物体的位置和方向。
- **机器人学:** 用于导航、抓取和与环境交互。

点云配准的主要挑战在于错误“**对应点**”的存在。这些对应点是指分别来自两个点云，但被错误地认为是同一个物理点的点对。这类异常值可能源于传感器噪声、场景中的动态物体或不完美的特征匹配算法。像迭代最近点（Iterative Closest Point, ICP）这样的传统方法对这些异常值非常敏感，很容易收敛到错误的对齐结果。

TEASER++ 经过专门设计，能够抵御大量的异常值，甚至宣称在异常值比例超过99%的情况下也能成功配准。

------

### TEASER++ 鲁棒性背后的方法论

TEASER++ 的卓越性能并非依赖单一技术，而是一个精心设计的流程，能够系统性地、高效地剔除异常值并求解变换。其核心方法可分解为以下几个关键步骤：

1. **生成平移不变测量值:** 第一步是将旋转和平移的估计解耦。TEASER++ 通过创建“**平移不变**”的测量值来实现这一点。对于源点云和目标点云中的每一对对应点 (p_i,q_i)，它会计算相对于某个中心点的差分向量，或者点对之间的差分向量。这有效地消除了未知平移量的影响。
2. **尺度估计 (可选但鲁棒):** TEASER++ 还可以求解两个点云之间未知的尺度因子。它通过计算每个点云中点对之间距离的比率来实现。通过在这些比率的直方图中寻找众数，可以鲁棒地估计出尺度，有效滤除被异常值污染的尺度估计。
3. **通过截断最小二乘法 (TLS) 和自适应投票进行旋转估计:** 最关键的步骤是旋转估计。TEASER++ 将此问题建模为**截断最小二乘法 (Truncated Least Squares, TLS)** 问题。其目标是找到一个旋转，使得一部分“内点”（inlier）对应点的平方误差和最小化，同时完全忽略异常值。为了高效求解，它采用了一种**自适应投票**方案。每个对应点都会为一个特定的旋转“投票”。通过将旋转空间离散化，TEASER++ 可以快速识别出一组对某个一致旋转达成共识的对应点集合。
4. **最大团裁剪 (Maximum Clique Pruning):** 为了进一步提纯内点集合，TEASER++ 构建了一个“**一致性图**”（consistency graph）。在这个图中，每个节点代表一个假定的对应点。如果在刚性变换的假设下，两个节点所代表的点对是相互一致的（即源点云中两点间的距离与目标点云中对应两点间的距离相似），那么这两个节点之间就会连接一条边。因此，寻找最大的一组相互一致的对应点的问题，就等价于在该图中寻找**最大团 (maximum clique)**。最大团代表了最大可能的内点集合。TEASER++ 使用一个高效的、并行的最大团求解器来完成这一任务。
5. **旋转和平移的精确求解:** 利用从最大团中识别出的内点，算法使用标准的**奇异值分解 (Singular Value Decomposition, SVD)** 方法来计算精确的旋转。对于一个干净的对应点集合，SVD方法在最小二乘意义上是最佳的。一旦确定了最优旋转，通过对齐内点集合的质心，就可以轻松计算出平移向量。
6. **可认证的最优性:** TEASER++ 的“可认证”特性源于其使用了**半定规划 (Semidefinite Programming, SDP) 松弛**。虽然核心的TEASER++算法本身已经非常快速和有效，但它可以与一个“认证器”相结合。该认证器会求解原始问题的一个松弛版本。如果这个松弛问题的解是“紧的”（tight），它就从数学上保证了所找到的旋转对于给定的对应点集合确实是**全局最优**的。在实践中，更快的、未经认证的TEASER++流程几乎总能找到这个最优解。

------

### 实践应用：实现与使用

TEASER++ 作为一个开源库提供，为了性能主要用 C++ 编写。它也为以下环境提供了便捷的封装：

- **Python:** 便于集成到流行的数据科学和机器人工作流中。
- **MATLAB:** 满足学术界和研究社区的需求。
- **ROS (机器人操作系统):** 方便在机器人系统中使用。

一个典型的工作流程包括：

1. **提供点云和初始对应点:** 用户提供两个点云和一组假定的对应点。这些对应点可以通过各种三维特征描述子（如FPFH, 3DSmoothNet）或简单的最近邻搜索生成。
2. **设置求解器参数:** 用户可以配置求解器，例如指定预期的噪声水平以及是否求解尺度。
3. **运行求解器:** 只需一个函数调用即可执行TEASER++的整个流程。
4. **获取结果:** 输出即为估计出的旋转矩阵、平移向量和尺度因子。

------

### 优势与局限性

**优势:**

- **极端鲁棒性:** 其主要优势是能够处理极高比例的异常值。
- **速度快:** 算法经过高度优化，比许多其他鲁棒配准方法快得多，通常在毫秒级内完成。
- **可认证的最优性:** 能够提供找到全局最优解的保证。
- **可扩展性:** 能够处理大量的对应点。
- **功能全面:** 可以同时求解三维旋转、平移和尺度。

**局限性:**

- **需要初始对应点:** TEASER++ 本身不是一个生成对应点的算法。它依赖于一个初始的、可能充满噪声的对应点集合。最终配准的质量仍然取决于初始集合中是否存在足够数量的真实内点。
- **理论复杂性:** 底层的数学原理，特别是涉及半定规划的可认证部分，比较深奥。但是，库的API将这种复杂性从最终用户那里抽象掉了。

总而言之，TEASER++ 代表了鲁棒点云配准领域的一大重要进展。通过巧妙地结合代数操作、鲁棒统计学和图论，它为三维视觉中的一个基础性问题提供了一个实用、快速且可靠的解决方案，为各种应用中的更鲁棒、更精确的感知系统提供了可能。

------

## 官方 GitHub 仓库

- https://github.com/MIT-SPARK/TEASER-plusplus

------

## 复现步骤：使用预打包环境与代码

### 1. 下载资源

- Docker 镜像:
  - **链接:** https://pan.baidu.com/s/1K2inNvFQcajOQZM8M7XbjA
  - **文件:** `teaserpp_dockerimage.tar`
- 示例代码:
  - **链接:** https://pan.baidu.com/s/1LafNxmlViU2mf-dGlZeiYQ
  - **文件:** `teaserpp-code.zip`

### 2. 操作步骤

1. 解压代码压缩包 `teaserpp-code.zip`。

2. 导入 Docker 镜像：

   Bash

   ```
   docker load < teaserpp_dockerimage.tar
   ```

3. 启动 Docker 容器，并将解压后的代码根目录映射到容器的 

   ```
   /app
   ```

    目录。

   - Linux / macOS:

     Bash

     ```
     docker run -it -v ./:/app teaserpp:latest /bin/bash
     ```

   - Windows (CMD):

     Bash

     ```
     docker run -it -v %cd%:/app teaserpp:latest /bin/bash
     ```

4. 此时您已进入 Docker 容器的交互式终端，进入挂载的代码目录：

   Bash

   ```
   cd /app
   ```
  ![img1](imgs/1748941047445.jpg)

1. 用于配准两个 PLY 文件的示例代码位于 

   ```
   examples/teaser_cpp_fpfh_ply/teaser_cpp_fpfh.cc
   ```

   。您可以修改文件中的第 61 和 67 行来指定您自己的 PLY 文件路径。

   ![img2](imgs/iShot_2025-06-03_17.00.39.png)

2. 将待配准的文件放入代码目录，并更新上述代码中的路径。

3. 编译并运行代码：

   Bash

   ```
   # 进入示例代码目录
   cd examples/teaser_cpp_fpfh_ply
   
   # 创建并进入build目录
   mkdir build
   cd build
   
   # 编译
   cmake ..
   make
   
   # 运行
   ./teaser_cpp_fpfh
   ```

### 3. 运行输出示例

Shell

```
root@0b1dbba57a95:/app/examples/teaser_cpp_fpfh_ply/build# ./teaser_cpp_fpfh 
    Read 16814134 total vertices 
    Read 26377700 total vertices 
正在对源点云进行下采样 (leaf_size: 0.2)...
下采样后源点云剩余 67893 个点。
正在对目标点云进行下采样 (leaf_size: 0.2)...
下采样后目标点云剩余 139545 个点。
正在保存下采样后的源点云到: downsampled_source.ply
正在保存下采样后的目标点云到: downsampled_target.ply
正在计算FPFH特征 (法线半径: 0.5, FPFH半径: 1.5)...
FPFH特征计算完毕。
源点云描述子数量: 67893
目标点云描述子数量: 139545
正在匹配特征 (使用相互对应检查: 是)...
CROSS CHECK
Skipping Tuple Constraint.
找到 5006 个初始对应点对。
开始使用 TEASER++ 进行配准...
Starting scale solver (only selecting inliers if scale estimation has been disabled).
Scale estimation complete.
Max core number: 596
Num vertices: 5007
Max Clique of scale estimation inliers: 
Using chain graph for GNC rotation.
Starting rotation solver.
GNC rotation estimation noise bound:3
GNC rotation estimation noise bound squared:9
GNC-TLS solver terminated due to cost convergence.
Cost diff: 0
Iterations: 17
Rotation estimation complete.
Starting translation solver.
Translation estimation complete.
=====================================
          TEASER++ Results           
=====================================
Estimated rotation: 
    0.76842    0.636905  -0.0623118
  -0.638254    0.769823 -0.00229025
  0.0465104   0.0415306    0.998054

Estimated translation: 
 -24.758
-15.3512
0.786257

正在变换下采样后的源点云...
正在保存变换后的源点云到: transformed_source_registered.ply
正在变换原始的源点云...
正在保存变换后的(原始)源点云到: transformed_source_original_registered.ply

配准完成。你可以比较以下文件：
1. 变换后的(下采样)源点云: transformed_source_registered.ply
2. 变换后的(原始)源点云: transformed_source_original_registered.ply
(也可以查看原始下采样版本: downsampled_target.ply 和 downsampled_source.ply)

初始对应点对数量: 5006
Time taken (s): 1.05065
=====================================
```

------

## DIY：从零开始制作 Docker 镜像

### 1. 制作步骤

1. 拉取基础 Ubuntu 镜像：

   Bash

   ```
   docker pull ubuntu
   ```

2. 启动一个交互式容器：

   Bash

   ```
   docker run -it ubuntu /bin/bash
   ```

3. 在容器内，安装所有必要的依赖：

   Bash

   ```
   apt-get update
   apt-get install -y git cmake build-essential libboost-all-dev libeigen3-dev pybind11-dev libpcl-dev
   ```

4. 从 GitHub 克隆 TEASER++ 源代码：

   Bash

   ```
   git clone https://github.com/MIT-SPARK/TEASER-plusplus.git
   ```

5. 编译并安装 TEASER++：

   Bash

   ```
   cd TEASER-plusplus
   mkdir build
   cd build
   cmake ..
   make -j4
   make install
   ```

6. （可选）验证安装是否成功：

   Bash

   ```
   cd ../examples/teaser_cpp_ply
   mkdir build
   cd build
   cmake ..
   make
   ./teaser_cpp_ply
   ```

7. 退出容器：

   Bash

   ```
   exit
   ```

8. 将容器保存为一个新的 Docker 镜像：

   Bash

   ```
   # (首先用 docker ps -a 找到刚才退出的容器ID)
   docker commit -m "teaser++ env" -a "your-name" <容器ID> teaserpp:latest
   ```

9. 将新镜像打包为 tar 文件以便分发：

   Bash

   ```
   docker save teaserpp:latest > teaserpp_dockerimage.tar
   ```

### 2. 自制镜像的使用方法

- 镜像下载 (备用地址):
  - **链接:** https://pan.baidu.com/s/15HxOJatiNzBDkiGMMN7Zbw?pwd=ad5a
  - **提取码:** `ad5a`

<!-- end list -->

1. 导入镜像: `docker load < teaserpp_dockerimage-aptpcl.tar`
2. 准备您的代码，例如 `TEASER-plusplus/examples` 目录。
3. 启动容器并挂载代码: `docker run -it -v /path/to/your/code:/app teaserpp:latest /bin/bash`
4. 进入容器内的挂载目录: `cd /app`
5. 进入示例目录: `cd teaser_cpp_ply`
6. 创建 build 目录: `mkdir build`
7. 进入 build 目录: `cd build`
8. 配置: `cmake ..`
9. 编译: `make`
10. 执行: `./teaser_cpp_ply`