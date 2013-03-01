JSONXSD2CPP := ../../../../jsonxsd2cpp.py
DATA_DIR := ../../data/simple_type
XSD_FILE := $(DATA_DIR)/type.xsd

SINGLE_ELEMENTS := $(shell grep -P 'element name="\S+[^s]"' $(XSD_FILE) | sed 's/^.*name="//' | sed 's/".*$$//')

test:
	@echo ""
	@echo "Expect no C++ code is generated on single basic type element"
	@echo ""
	for d in $(SINGLE_ELEMENTS); do \
		$(JSONXSD2CPP) --element=$${d} --gentest $(XSD_FILE); \
		ls *.h *.cpp 1>/dev/null 2>&1 || continue; \
		echo "Fail on $${d}"; exit 1; \
	done;

clean:
	rm -f *.h *.cpp
