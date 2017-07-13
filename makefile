all: dist/prepared

dist/prepared: setup.py dmoea/Constants.py dmoea/Functions.py dmoea/Sampling.py dmoea/Sorting.py dmoea/Structures.py dmoea/__init__.py README.rst
	python setup.py sdist && python setup.py bdist_wheel --universal && touch dist/prepared
	
README.rst: README.md
	python -c "$$(printf "with open('README.md', 'r') as fp:\n    for line in fp:\n        if 'Advertisement' in line: break\n        print(line.strip())\n")" | pandoc -o README.rst
