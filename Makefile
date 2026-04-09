.PHONY: help build preview deploy clean install

# Export empty passphrase for Pulumi
export PULUMI_CONFIG_PASSPHRASE=

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install "pyavd[ansible]==6.1.0" pulumi pyeapi pyyaml

build: ## Generate AVD configurations using PyAVD
	@echo "🚀 Building configurations with PyAVD..."
	@python build.py

preview: build ## Build configs and preview Pulumi changes
	@echo "👀 Previewing Pulumi deployment..."
	@pulumi preview

deploy: build ## Build configs and deploy with Pulumi
	@echo "🚀 Deploying with Pulumi..."
	@pulumi up --yes

refresh: ## Refresh Pulumi state
	@pulumi refresh --yes

clean: ## Clean generated files
	@echo "🧹 Cleaning generated files..."
	@rm -rf intended/ documentation/
	@echo "✅ Clean complete"

rebuild: clean build ## Clean and rebuild all configs

status: ## Show Pulumi stack status
	@pulumi stack

diff: build ## Show diff of what would change
	@pulumi preview --diff

validate: ## Validate inventory and configs
	@echo "✅ Validating inventory..."
	@python -c "import yaml; yaml.safe_load(open('inventory.yml'))" && echo "  ✓ inventory.yml is valid"
	@python -c "import yaml; yaml.safe_load(open('group_vars/FABRIC.yml'))" && echo "  ✓ FABRIC.yml is valid"
	@python -c "import yaml; yaml.safe_load(open('group_vars/SPINES.yml'))" && echo "  ✓ SPINES.yml is valid"
	@python -c "import yaml; yaml.safe_load(open('group_vars/LEAFS.yml'))" && echo "  ✓ LEAFS.yml is valid"

check-configs: build ## Check that configs were generated
	@echo "📁 Checking generated configs..."
	@ls -lh intended/configs/*.cfg | awk '{print "  ✓", $$9, "-", $$5}'

.DEFAULT_GOAL := help
