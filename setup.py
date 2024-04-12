import setuptools


setuptools.setup(
    name='llonebot',
    version='1.0.0',
    author='格索伊',
    author_email='719893361@qq.com',
    description='NTQQ llonebot插件 python交互包',
    packages=setuptools.find_packages(),
    install_requires=[
        'websockets',
        'pydantic',
    ],
    python_requires='>=3.7'
)
