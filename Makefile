
format:
	@black .

isort:
	@isort .

optimise-imports:
	@autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports module02

pretty: optimise-imports isort format

lint:
	@pylint --rcfile=setup.cfg module02

typecheck:
	mypy --show-error-codes .

importcheck:
	@pylint --disable=all --enable=unused-import module02

stylecheck:
	@black --check module02
	@isort --check-only module02
	@flake8 module02

check: stylecheck typecheck lint