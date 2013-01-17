JSONGENERATOR := ../../jsoncppgenerator.py
JSON_DIR := ../data

JSON_FILES := $(wildcard $(JSON_DIR)/null/*.json)

test_null:
	@echo ""
	@echo "Expect failure with JSON data files having null element or empty object/array"
	@echo ""
	for d in $(JSON_FILES); do \
		$(JSONGENERATOR) --jsondatafile=$${d} 2>/dev/null || continue; \
		echo "Fail on $${d}"; exit 1; \
	done;

clean:
	rm -f *.h *.cpp
