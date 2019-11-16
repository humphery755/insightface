https://github.com/deepinsight/insightface
https://www.cnblogs.com/zyly/p/9703614.html
model: https://pan.baidu.com/s/1knmJxbNKMzJJ3SvofP4K0A  code: cxdu 

apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev libedit-dev

git clone https://github.com/pyenv/pyenv.git ~/.pyenv

vi ~/.bashrc
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

pyenv update

pyenv install 3.6.9
pyenv versions
pyenv global 3.6.9
mkdir ~/.pip/
vi ~/.pip/pip.conf
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple

python -m pip install --upgrade pip

pip install opencv-python numpy mxnet easydict scipy scikit-image sklearn tornado
