# developer Makefile
#

.PHONY: docs all clean

TESTCMD=nosetests -s --with-doctest gsTiles tests
MAKECMD=make

# Note: docs will not build if tests fail, reverse order to change behavior.
all: coverage docs

test:
	$(TESTCMD)
coverage:
	#rm -rf cover/*
	$(TESTCMD) --with-coverage --cover-package=gsTiles,tests --cover-tests --cover-html --cover-html-dir=docs/.build/html/cover
docs:
	#rm docs/source/api/*.rst
	sphinx-apidoc -f -e -o docs/api gsTiles
	cd docs && make html
clean:
	find . -name "*.pyc" |xargs rm
	rm dist/gsTiles-*.tar.gz
dist: clean setup.py
	python setup.py sdist
	twine upload dist/*
