.git/hooks/pre-commit:
	pre-commit install

install_precommit: .git/hooks/pre-commit

test_precommit: install_precommit
	pre-commit run --all-files

precommit: install_precommit
	pre-commit run
