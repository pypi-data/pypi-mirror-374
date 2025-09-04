## Build
-> create venv and activate
(install meta)
-> pip install setuptools wheel twine
(build package)
-> python setup.py sdist bdist_wheel
-> pip install dist/rule-engine-core-0.1.0-py3-none-any.whl
(Publish to pypi)
-> pip install twine
-> twine upload dist/*

### Docker
-> `psql --username=$POSTGRES_USER -d $POSTGRES_DB`