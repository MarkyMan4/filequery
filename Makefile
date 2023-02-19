# for build and deploy, must be in an environment with requirements from requirements-dev.txt installed

# create a build - outputs to dist directory
build:
	python -m build

# upload to pypi
deploy:
	twine upload dist/*

# install package from local and run unit tests
test:
	pip install .
	python tests/test_filequery.py
	pip uninstall filequery -y
