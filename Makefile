# AI Buddy Makefile
# Phony targets to ensure they always run
.PHONY: demo test seed report-all bundle verify

# Default target
all: test

# Run Streamlit demo
demo:
	streamlit run streamlit_app.py

# Run tests
test:
	pytest -q

# Seed history data
seed:
	python scripts/seed_history.py

# Generate reports for all children
report-all:
	python -m ai_buddy.report --all --period 7d --format both

# Bundle demo data
bundle:
	python scripts/export_demo_bundle.py

# Verify Phase 5
verify:
	python verify_phase5.py

# Help target
help:
	@echo "Available targets:"
	@echo "  demo      - Run Streamlit demo app"
	@echo "  test      - Run pytest tests"
	@echo "  seed      - Seed history data"
	@echo "  report-all - Generate reports for all children"
	@echo "  bundle    - Export demo bundle"
	@echo "  verify    - Verify Phase 5"
	@echo "  help      - Show this help message"
