.PHONY: help build preview deploy clean install

# Export empty passphrase for Pulumi
export PULUMI_CONFIG_PASSPHRASE=

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	pip install -r requirements.txt

build: ## Generate AVD configurations using PyAVD
	@echo "🚀 Building configurations with PyAVD..."
	@python build.py

preview: ## Preview Pulumi changes (auto-generates configs)
	@echo "👀 Previewing Pulumi deployment (configs auto-generated)..."
	@pulumi preview

deploy: ## Deploy with Pulumi (auto-generates configs)
	@echo "🚀 Deploying with Pulumi (configs auto-generated)..."
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

format: ## Format Python and Markdown files
	@echo "🎨 Formatting Python files with ruff..."
	@ruff format *.py
	@echo "🎨 Formatting Markdown files with mdformat..."
	@mdformat *.md
	@echo "✅ Formatting complete!"

lint: ## Lint Python files with ruff
	@echo "🔍 Linting Python files..."
	@ruff check *.py

lint-fix: ## Lint and fix Python files
	@echo "🔧 Linting and fixing Python files..."
	@ruff check *.py --fix

.DEFAULT_GOAL := help
