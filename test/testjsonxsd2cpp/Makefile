SUBDIRS = autotest

.PHONY: $(SUBDIRS)
build: $(SUBDIRS)

autotest:
	make --directory=$(@)

clean:
	for d in $(SUBDIRS); do \
		make clean --directory=$${d}; \
	done

