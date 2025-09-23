
conda create -n ml-aspanformer python=3.10

conda activate ml-aspanformer

pip install 如下内容
```
albumentations==0.5.1 --no-binary=imgaug,albumentations
ray>=1.0.1
einops==0.3.0
tqdm
autopep8
pylint
ipython
jupyterlab
matplotlib
h5py
install torch torchvision --index-url https://download.pytorch.org/whl/cu126
pytorch-lightning
kornia
```