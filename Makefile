.PHONY: zip-artifact
zip-artifact:
	rm -f artifact/artifact.zip
	zip artifact/artifact.zip artifact/fruit.py
