VERSION_BUMP ?= patch

build:
	uv version --bump $(VERSION_BUMP) # or minor/major
	uv build

publish:
	uv publish --token $(PYPI_TOKEN)

clean:
	rm -rf ./dist