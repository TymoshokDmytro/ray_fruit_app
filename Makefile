.PHONY: zip-artifact
zip-artifact:
	rm artifact/artifact.zip
	zip artifact/artifact.zip artifact/fruit.py
