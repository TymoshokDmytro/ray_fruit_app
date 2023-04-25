.PHONY: deploy-manifest
deploy-manifest:
	kubectl apply -f ray_serve_fruit.yaml

.PHONY: delete-ray-service
delete-ray-service:
	kubectl delete rayservices.ray.io rayservice-sample

.PHONY: port-forward
port-forward:
	kubectl port-forward svc/rayservice-sample-serve-svc 8000:8000

.PHONY: ray-start
ray-start:
	ray start --head --port=6379 --dashboard-port=8265 --dashboard-host=0.0.0.0  # ray stop

.PHONY: serve-start
serve-start:
	serve start  --http-host='0.0.0.0'  # serve shutdown

.PHONY: kafka-start
kafka-start:
	docker-compose up -d

.PHONY: kafka-stop
kafka-stop:
	docker-compose down