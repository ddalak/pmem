pmem
====

Draw process memory map in dot lenguage. It then can be converted 
to any image format e.g. svg thanks to graphviz (http://www.graphviz.org/).

Example usage:

`./pmem.py -p pid_number`

`dot -Tsvg 3752_1413807109.03.dot > sleep.svg`

or

`dot -Tpng 3752_1413807109.03.dot > sleep.png`

![:map file example](/sleep.png)


