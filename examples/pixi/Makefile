# Copyright 2023 Roman Hlushko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

CLUSTER?=pixishop
REGISTRY_PORT?=1800
SOURCE?=common services

.PHONY: help

help:
	@echo "💎Pixi Jewelery Shop"
	@echo "Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

cluster-start:  ## Start the cluster
	@k3d cluster create $(CLUSTER) --agents 2 \
		--registry-create $(CLUSTER)-registry:0.0.0.0:$(REGISTRY_PORT) \
		-p "8888:80@loadbalancer" \
		--kubeconfig-update-default --kubeconfig-switch-context

cluster-ctx:  ## Configure the cluster context
	@kubectl config set current-context k3d-$(CLUSTER)

cluster-stop: ## Stop the cluster
	@k3d cluster delete $(CLUSTER)

start: cluster-ctx ## Start the whole system
	@tilt up

image: ## Build the image
	@docker build -t pixi/service:dev -f Dockerfile .

lint: ## Lint source code
	@poetry run black $(SOURCE)
	@poetry run ruff --fix $(SOURCE)
	@poetry run mypy --pretty $(SOURCE)

