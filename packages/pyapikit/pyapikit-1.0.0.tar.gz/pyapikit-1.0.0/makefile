.PHONY: install build upload upload-test upload-mirror upload-company clean

env:
	. ~/venvs/py38_xingyun/bin/activate

install:  # 安装
	pip install -e .

build:  # 构建
	export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple/;\
	python -m build

upload:  # 上传到 PyPI
	twine upload dist/* --repository pypi --verbose

# 导出requirements.txt, 需要安装pip-tools， 仅仅导出运行时依赖
export_requirements:  
	pip-compile pyproject.toml -o requirements.txt

upload-xmov:  # 上传到自定义镜像源
	twine upload dist/* --repository xmov  --verbose

clean:  # 清理
	rm -rf build dist
	rm -rf *.egg-info

all:  # 上传到所有镜像源
	make clean
	make build
	make upload

help:  # 帮助
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  install: 安装依赖"
	@echo "  build: 构建"
	@echo "  upload: 上传到 PyPI"
	@echo "  upload-xmov: 上传到自定义镜像源"
	@echo "  clean: 清理"
	@echo "  all: 清理，构建并上传到pypi镜像源"
	@echo "  docs-build: 构建文档"
	@echo "  docs-clean: 清理文档"
	@echo "  docs-serve: 本地预览文档（http://localhost:8000）"

test:  # 测试
	PYTHONPATH=. pytest -v -s

test_some:  # 测试
	PYTHONPATH=. pytest -v -s tests/test_dotdict.py::TestDotDict::test2

push_xmov:
	git push origin

push_gitee:  # 推到gitee上
	git push gitee

# 文档相关命令
docs-build:  # 构建文档
	cd docs && make html

docs-clean:  # 清理文档
	cd docs && make clean

docs-serve:  # 本地预览文档
	cd docs/build/html && python -m http.server 8000
