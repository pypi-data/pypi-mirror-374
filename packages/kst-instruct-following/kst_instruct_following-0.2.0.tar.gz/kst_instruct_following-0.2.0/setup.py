from setuptools import setup, find_packages

setup(
    name='kst_instruct_following',          # 包名（必须唯一）
    version='0.2.0',                   # 版本号
    author='zhongp',
    author_email='1658763666@qq.com',
    description='src for kst_instruct_following',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),          # 自动查找所有模块
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[                 # 依赖项列表
        # 'requests>=2.25.1',
    ],
)