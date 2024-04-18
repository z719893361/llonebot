import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='llonebot',
    version='1.0.4',
    author='Gesoy',
    author_email='719893361@qq.com',
    description='NTQQ LLOneBot 插件交互工具',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/z719893361/llonebot",
    project_urls={
        "Bug Tracker": "https://github.com/z719893361/llonebot/issues",
    },
    packages=setuptools.find_packages(),
    install_requires=[
        'websockets',
        'pydantic',
        'aiocron'
    ],
    python_requires='>=3.7'
)
