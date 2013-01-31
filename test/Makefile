SUBDIRS = depends/json_spirit autotest nulltest

.PHONY: depends/json_spirit autotest nulltest
build: autotest nulltest

depends/json_spirit:
	make --directory=$(@)

autotest: depends/json_spirit
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

