test:
	python setup.py test

runserver:
	./demo/run-stub-server.py -l demo/servers.txt -r demo/responses.txt -t demo/stubs

nohup_runserver:
	# python -u to force stdin, stdout and stderr to be totally unbuffered so that nohup.out could show the output.
	nohup python -u demo/run-stub-server.py -l demo/servers.txt -r demo/responses.txt -t demo/stubs 2>&1 &

stopserver:
	pgrep -f "python ./demo/run-stub-server.py" | xargs kill

build:
	python setup.py build

install:
	python setup.py install

clean:
	rm -rf build dist easy_rate.egg-info nohup.out demo/stubs/*.json

PYVER ?= 3.7.1
REQ ?= requirements.txt
NAME ?= easy_rate
prepare_virutalenv:
	pyenv install $(PYVER) -s
	-pyenv virtualenv $(PYVER) ${NAME}
	source `pyenv virtualenv-prefix ${NAME}`/envs/${NAME}/bin/activate
	`pyenv virtualenv-prefix ${NAME}`/envs/${NAME}/bin/pip install -r $(REQ)
