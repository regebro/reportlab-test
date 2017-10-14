RL_VERSION = 3.4.0


all: ve test

ve:
	virtualenv ve
	ve/bin/pip install reportlab==$(RL_VERSION) z3c.rml

test:
	ve/bin/python reportlab-test.py
