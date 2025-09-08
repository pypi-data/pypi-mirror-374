# syTool

#### 介绍
常用工具类

#### 软件架构
软件架构说明


#### 安装教程

1.  xxxx
2.  xxxx
3.  xxxx

#### 使用说明

1.  xxxx
2.  xxxx
3.  xxxx

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 发布
1. 更新版本号​​：在 pyproject.toml中更新 version字段（例如从 0.1.0到 0.1.1）。遵循语义化版本控制
2. 构建分发包
```shell
# 安装 build 工具
pip install build
# 在项目根目录下执行命令
python -m build  # 生成 dist/syTool-0.1.0-py3-none-any.whl 和 .tar.gz
```
3. 上传到 TestPyPI（测试）
```shell
twine upload --repository testpypi dist/*
# 测试安装
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple syTool[http]
```
4. 上传到 PyPI（正式）
```shell
twine upload dist/*
```
