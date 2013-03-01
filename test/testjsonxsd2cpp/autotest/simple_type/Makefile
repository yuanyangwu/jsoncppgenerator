JSONXSD2CPP := ../../../../jsonxsd2cpp.py
DATA_DIR := ../../data/simple_type
XSD_FILE := $(DATA_DIR)/type.xsd
JSON_FILES := $(wildcard $(DATA_DIR)/*.json)

TEST_DIRS := $(patsubst $(DATA_DIR)/%.json, %, $(JSON_FILES))

default: run

run: compile
	@echo ""
	@echo "Run cases"
	@echo ""
	for d in $(TEST_DIRS); do \
		make --directory=$${d} run; \
	done;

compile: generate_cases
	@echo ""
	@echo "Compile cases"
	@echo ""
	for d in $(TEST_DIRS); do \
		make --directory=$${d}; \
	done;

generate_cases: $(TEST_DIRS)

%: $(DATA_DIR)/%.json
	mkdir -p $(@)/src
	$(JSONXSD2CPP) --element=$(@) --dstdir=$(@)/src $(JSON_GENERATOR_OPTIONS) --gentest $(XSD_FILE)
	sed 's/TO_REPLACE_JSON_FILE/$(subst /,\/,$(^))/g' Makefile.template > $(@)/Makefile

clean:
	rm -fr $(TEST_DIRS)

