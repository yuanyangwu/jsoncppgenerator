SUBDIRS = depends/json_spirit autotest nulltest

build:
	for d in $(SUBDIRS); do \
		make --directory=$${d}; \
	done

clean:
	for d in $(SUBDIRS); do \
		make clean --directory=$${d}; \
	done

