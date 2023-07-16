lint:
	docker run --rm --user=$(shell id -u):$(shell id -g) -e "LINT_FOLDER_PYTHON=." -v $(CURDIR):/app divio/lint /bin/lint ${ARGS}
