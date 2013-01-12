JSONGENERATOR := ../../jsoncppgenerator.py
JSON_DIR := ../data

JSON_FILES := \
	$(JSON_DIR)/object_simple.json \
	$(JSON_DIR)/object_object.json \
	$(JSON_DIR)/object_array.json \
	$(JSON_DIR)/array_simple.json \
	$(JSON_DIR)/array_object.json \
	$(JSON_DIR)/array_array_simple.json \
	$(JSON_DIR)/array_array_object.json \

CASE_ROOT_DIR := cases

TEST_DIRS := $(patsubst $(JSON_DIR)/%.json, $(CASE_ROOT_DIR)/%, $(JSON_FILES))

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

$(CASE_ROOT_DIR)/%: $(JSON_DIR)/%.json
	mkdir -p $(@)/src
	$(JSONGENERATOR) --jsondatafile=$(^) --dstdir=$(@)/src --gentest
	sed 's/TO_REPLACE_JSON_FILE/$(subst /,\/,$(^))/g' Makefile.template > $(@)/Makefile

clean:
	rm -fr $(CASE_ROOT_DIR)

