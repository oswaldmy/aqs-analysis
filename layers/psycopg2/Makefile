define SLSIGNORE
**/*.a
**/*.la
share/**
include/**
bin/**
endef
export SLSIGNORE

clean:
	rm -rf requirements.txt
	rm -rf layer*

deps:
	pipenv install
	pipenv lock -r > requirements.txt
	pip install -r requirements.txt --target ./layer/python/
	rm requirements.txt

slim:
	find . -name '*~' -exec rm -f {} +
	find . -name '*.log*' -delete
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name 'tests' -exec rm -rf {} +
	find . -name '**/*.pyc' -exec rm -rf {} +

slsignore:
	$(file > layer/.slsignore,$(SLSIGNORE))

build: clean deps slim

deploy: build slsignore
	sls deploy

zip: build
	cd layer; zip -r ../../$(notdir $(basename ${PWD})).zip ./python;	cd ..
