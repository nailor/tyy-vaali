RST := $(shell find \
		doc \
		-name '*.rst' \
		\! -name '.*' \
		\! -name '_*' \
		-printf '%p\n' \
	| sort \
	)

### reStructuredText
HTML := $(RST:%.rst=%.html)

all:: $(HTML)

%.html: %.rst
	rst2html --halt=3 $< >$@.tmp
	mv $@.tmp $@

clean::
	rm -f doc/*.html README.html

