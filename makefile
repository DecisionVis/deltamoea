all: dist/prepared

dist/prepared: makefile setup.py deltamoea/Constants.py deltamoea/Functions.py deltamoea/Sampling.py deltamoea/Sorting.py deltamoea/Structures.py deltamoea/__init__.py README.rst
	python setup.py sdist --formats gztar,zip && python setup.py bdist_wheel --universal && touch dist/prepared
	
README.rst: README.md
	python -c "$$(printf "with open('README.md', 'r') as fp:\n    for line in fp:\n        if 'Advertisement' in line: break\n        print(line.strip())\n")" | pandoc -o README.rst
