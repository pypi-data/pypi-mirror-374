#wxapi

1.创建文件 $HOME/.pypirc


[distutils]
index-servers = 
    pypi

[pypi]
username = __token__
password = your-api-token


#在终端或命令行中执行以下命令来安装 wheel
pip install wheel

#运行打包命令
python setup.py sdist bdist_wheel

#发送命令
twine upload dist/*

#升级包
pip install --upgrade wxswutilsapi

pip install wxswutilsapi --upgrade --index-url https://pypi.org/simple

