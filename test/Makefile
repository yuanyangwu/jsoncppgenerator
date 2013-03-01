SUBDIRS = depends/json_spirit testjsondata2cpp testjsonxsd2cpp

.PHONY: $(SUBDIRS)
build: testjsondata2cpp testjsonxsd2cpp

depends/json_spirit:
	make --directory=$(@)

testjsondata2cpp: depends/json_spirit
	make --directory=$(@)

testjsonxsd2cpp: depends/json_spirit
	make --directory=$(@)

clean:
	for d in $(SUBDIRS); do \
		make clean --directory=$${d}; \
	done

