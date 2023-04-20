.PHONY: zip-artifact
zip-artifact:
	rm -f artifact.zip
	zip artifact.zip fruit.py

.PHONY: deploy-manifest
deploy-manifest:
	kubectl apply -f ray_serve.yaml