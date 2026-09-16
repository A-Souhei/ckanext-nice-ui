.PHONY: css clean-tailwind

# Tailwind's standalone CLI: one binary, no npm. Pinned and checksum-verified,
# then run in a throwaway container with no network and only this repository
# mounted — the compiled CSS is committed, so nothing else ever needs it.
TAILWIND_VERSION := v4.3.3
ARCH := $(shell uname -m)
ifeq ($(ARCH),x86_64)
TAILWIND_ASSET  := tailwindcss-linux-x64
TAILWIND_SHA256 := dc61b3ac6b8c9ca874c0cc4c57b2409791a64c5540404ca5f5367360babc313a
else ifeq ($(ARCH),aarch64)
TAILWIND_ASSET  := tailwindcss-linux-arm64
TAILWIND_SHA256 := 55fd0b241214eff3de1e8ee4f22796662f2d2e7a49bcfca7477cfd0bac398195
else
$(error unsupported architecture $(ARCH))
endif

TAILWIND := .tailwind/$(TAILWIND_ASSET)-$(TAILWIND_VERSION)
OUTPUT   := ckanext/nice_ui/assets/nice-ui.css

css: $(TAILWIND)
	docker run --rm --network none --user "$$(id -u):$$(id -g)" \
		-v "$(CURDIR):/src" -w /src debian:bookworm-slim \
		/src/$(TAILWIND) --input tailwind/input.css --output $(OUTPUT) --minify
	@echo "compiled $(OUTPUT) ($$(wc -c < $(OUTPUT)) bytes)"

$(TAILWIND):
	@mkdir -p .tailwind
	curl -fsSL -o $@.part \
		https://github.com/tailwindlabs/tailwindcss/releases/download/$(TAILWIND_VERSION)/$(TAILWIND_ASSET)
	echo "$(TAILWIND_SHA256)  $@.part" | sha256sum --check --strict
	chmod +x $@.part && mv $@.part $@

clean-tailwind:
	rm -rf .tailwind
