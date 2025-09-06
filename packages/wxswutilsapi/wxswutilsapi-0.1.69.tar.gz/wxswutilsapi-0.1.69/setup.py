from setuptools import setup, find_packages

setup(
    name='wxswutilsapi',  # 库的名称
    version='0.1.69',  # 库的版本号
    packages=find_packages(),  # 自动查找所有包
    install_requires=[],  # 如果有依赖库的话
    tests_require=[
        'unittest',  # 或者 pytest
    ],
    test_suite='tests',  # 指定测试目录
    author='liudaiyi',
    author_email='121274222@qq.com',
    description='python 工具库',  # 库的简短描述
    long_description=open('README.md', encoding='utf-8').read(),  # 显式指定编码
    long_description_content_type='text/markdown',  # 说明 long_description 内容的类型
    classifiers=[  # 用于指定一些分类标签，方便查找
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',  # 支持的 Python 版本
)
