test:
	export TESTING=1 && python3 manage.py create_db && pytest -c pytest.ini apps/ tests/ && python3 manage.py drop_db

migration:
	python3 manage.py db upgrade && python3 manage.py db migrate