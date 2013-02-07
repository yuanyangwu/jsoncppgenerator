SUBDIRS = autotest nulltest

.PHONY: autotest nulltest
build: autotest nulltest

autotest:
	# std::string
	# no namespace
	make --directory=$(@) JSON_GENERATOR_OPTIONS=""
	make clean --directory=$(@)
	# namespace
	make --directory=$(@) JSON_GENERATOR_OPTIONS="--namespace=com::test::json"
	make clean --directory=$(@)
	# std::wstring
	# no namespace
	make --directory=$(@) JSON_GENERATOR_OPTIONS="--stringtype=std::wstring"
	make clean --directory=$(@)
	# namespace
	make --directory=$(@) JSON_GENERATOR_OPTIONS="--namespace=com::test::json --stringtype=std::wstring"
	make clean --directory=$(@)

nulltest:
	make --directory=$(@)

clean:
	for d in $(SUBDIRS); do \
		make clean --directory=$${d}; \
	done

