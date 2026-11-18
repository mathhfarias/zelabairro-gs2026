.PHONY: run test
run:
	python -m flask --app wsgi run --debug

test:
	python -m unittest discover -s tests -v
