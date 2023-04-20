.PHONY: zip-artifact
zip-artifact:
	rm -f artifact.zip
	zip artifact.zip fruit.py
