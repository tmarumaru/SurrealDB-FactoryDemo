
IMAGE   :=  "factory-demo"

.PHONY: build
build:
	docker build -t $(IMAGE) -f ./Dockerfile .

.PHONY: clean
clean:
	docker system prune
	docker volume prune


