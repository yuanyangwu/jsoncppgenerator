SUBDIRS = basic_type single_basic_type \
	simple_type single_simple_type \
	complex_type \


.PHONY: $(SUBDIRS)
build: $(SUBDIRS)

basic_type simple_type complex_type:
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

single_basic_type single_simple_type:
	make --directory=$(@)

clean:
	for d in $(SUBDIRS); do \
		make clean --directory=$${d}; \
	done

