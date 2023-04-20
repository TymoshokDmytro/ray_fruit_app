.PHONY: zip-artifact
zip-artifact:
	rm -f artifact.zip
	zip artifact.zip fruit.py

.PHONY: deploy-manifest
deploy-manifest:
	kubectl apply -f ray_serve_fruit.yaml

.PHONY: delete-ray-service
delete-ray-service:
	kubectl delete rayservices.ray.io rayservice-sample

.PHONY: port-forward
port-forward:
	kubectl port-forward svc/rayservice-sample-serve-svc 8000:8000
