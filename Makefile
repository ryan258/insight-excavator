.PHONY: test backup restore-check

# every test_*.py is a plain script that exits non-zero on failure; no network, no API key
test:
	@for t in test_*.py; do python3 $$t || exit 1; done; echo "all self-checks passed"

# sources/ is gitignored and cost real API spend to build — the filter is stochastic,
# so it cannot be regenerated. The tarball holds everything that is state: sources, the
# resume logs, the dig ledger, your config, and the vault folder of kept notes.
# Copy it somewhere that is not this machine.
backup:
	@out="$(HOME)/idea-digger-backup-$$(date +%F).tgz"; \
	vault=$$(python3 -c "import json,os;print(os.path.expanduser(json.load(open('config.json'))['vault']))" 2>/dev/null); \
	files=""; for f in sources import-seen.log import-technique.log retag-commerce.log digs.jsonl config.json "$$vault"; do \
	  [ -n "$$f" ] && [ -e "$$f" ] && files="$$files $$f"; done; \
	tar czf "$$out" $$files 2>/dev/null && echo "wrote $$out"

# the newest backup must list its sources and notes; run this after `make backup`
restore-check:
	@b=$$(ls -t $(HOME)/idea-digger-backup-*.tgz | head -1); \
	echo "$$b"; tar tzf "$$b" | grep -c 'sources/.*\.txt$$' | sed 's/$$/ source files/'; \
	tar tzf "$$b" | grep -c '\.md$$' | sed 's/$$/ vault notes/'
