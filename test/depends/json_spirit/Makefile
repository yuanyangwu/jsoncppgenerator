
default: build_dist

download:
	if [ ! -f output/download/master.zip ]; then \
	  mkdir -p output/download && \
	  wget https://github.com/geli1988/json-spirit/archive/master.zip --directory-prefix=output/download; \
	fi

extracted: download
	if [ ! -d output/extracted ]; then \
	  mkdir -p output/extracted; \
	  unzip -q output/download/master.zip -d output/extracted; \
	fi

build_src: extracted
	if [ ! -f output/build/Makefile ]; then \
	  mkdir -p output/build/src && \
	  cp output/extracted/json-spirit-master/json_spirit/* output/build/src && \
	  cp Makefile.json_spirit output/build/Makefile; \
	fi
	make --directory=output/build

build_dist: build_src
	if [ ! -d output/dist/include ]; then \
	  mkdir -p output/dist/lib && \
	  cp output/build/output/bin/libjson_spirit.a output/dist/lib/ && \
	  mkdir -p output/dist/include && \
	  cp output/build/src/*.h output/dist/include/; \
	fi

clean:
	rm -fr output

