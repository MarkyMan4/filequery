# for build and deploy, must be in an environment with requirements from requirements-dev.txt installed

# create a build - outputs to dist directory
build-pkg:
	python -m build

# upload to pypi
deploy:
	twine upload dist/*

test:
	python tests/test_filequery.py

clean:
	rm -rf dist/ build/ __pycache__/ src/filequery.egg-info/
