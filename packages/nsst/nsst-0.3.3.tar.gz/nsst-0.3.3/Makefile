SHELL := /bin/bash
VERSION := $(shell uv version --short)

test:
	uv run pytest

tag:
	git tag -a v$(VERSION) -m "Release $(VERSION)"

release: test tag
	git push origin v$(VERSION)
