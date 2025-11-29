# Setup the Enviroment with python and conda

```shell
conda create -n condaEnvName python=3.10
source activate condaEnvName 
```

```shell
conda config --env --add channels conda-forge
conda install numpy
conda install -c conda-forge matplotlib
```

Install pytorch
- only CPU
  ```shell
  conda install pytorch torchvision torchaudio cpuonly -c pytorch
- With GPU
  ```shell
  conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia
- alternativ:
  ```shell
  pip3 install torch torchvision torchaudio

```shell
conda install -c conda-forge psutil
conda install -c auto pyswarm
conda install -c anaconda pandas
conda install -c anaconda openpyxl
```
