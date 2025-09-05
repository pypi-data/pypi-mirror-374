.PHONY: clean resource

SHELL=/bin/bash

RCC5 = pyrcc5
RCC6 = /usr/lib64/qt6/libexec/rcc

resource: resource/gui.qrc
	$(RCC5) -o ufit/guires_qt5.py $<
	$(RCC6) -g python $< | sed s,PySide6,PyQt6, > ufit/guires_qt6.py

clean:
	rm -rf build
	find . -name '*.pyc' -print0 | xargs -0 rm -f
