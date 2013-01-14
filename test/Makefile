SUBDIRS = depends/json_spirit autotest

build:
	for d in $(SUBDIRS); do \
		make --directory=$${d}; \
	done

clean:
	for d in $(SUBDIRS); do \
		make clean --directory=$${d}; \
	done

