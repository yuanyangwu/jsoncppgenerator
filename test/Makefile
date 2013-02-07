SUBDIRS = depends/json_spirit testjsondata2cpp

.PHONY: depends/json_spirit testjsondata2cpp
build: testjsondata2cpp

depends/json_spirit:
	make --directory=$(@)

testjsondata2cpp: depends/json_spirit
	make --directory=$(@)

clean:
	for d in $(SUBDIRS); do \
		make clean --directory=$${d}; \
	done

