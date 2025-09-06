SHELL = /bin/bash
MAKEFLAGS += --silent

PACKAGING_VENV_PATH=./venv_packaging
PACKAGING_REQUIREMENTS_PATH=./requirements.packaging.txt


all: build publish


setup: .check_minimal_config .setup_dependencies


build: setup
	source $(PACKAGING_VENV_PATH)/bin/activate; \
    rm -rf dist; \
	python -m build;


publish: setup
	source $(PACKAGING_VENV_PATH)/bin/activate; \
	python -m twine upload -r pypi dist/*;


.check_minimal_config:
	if ! which python3.10 >/dev/null; then \
    	echo "You have to install at least Python3.10."; \
    	exit 0; \
	fi


.setup_dependencies:
	if [ ! -d $(PACKAGING_VENV_PATH) ]; then \
		echo "No venv found, setting one"; \
		python3.10 -m venv $(PACKAGING_VENV_PATH); \
		source $(PACKAGING_VENV_PATH)/bin/activate; \
		echo "Venv setup OK"; \
		echo "Starting $(PACKAGING_REQUIREMENTS_PATH) installation"; \
		pip install -r $(PACKAGING_REQUIREMENTS_PATH); \
		echo "$(PACKAGING_REQUIREMENTS_PATH) installation is finished"; \
	fi


.PHONY: build publish .check_minimal_config .setup_dependencies
