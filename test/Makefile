SUBDIRS = depends/json_spirit autotest nulltest

.PHONY: depends/json_spirit autotest nulltest
build: autotest nulltest

depends/json_spirit:
	make --directory=$(@)

autotest: depends/json_spirit
	make --directory=$(@)

nulltest:
	make --directory=$(@)

clean:
	for d in $(SUBDIRS); do \
		make clean --directory=$${d}; \
	done

