
install:
	@echo "Installing package in editable mode..."
	uv tool install . -e
	@echo "Package installed in editable mode."
	ide-rules --help

pex:
	@echo "Building PEX binary..."
	@mkdir -p dist
	uvx pex . -c ide-rules -o dist/ide-rules.pex --interpreter-constraint "CPython>=3.12"
	@echo "Built dist/ide-rules.pex"
