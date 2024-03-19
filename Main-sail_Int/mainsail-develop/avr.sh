#!/bin/bash
cd simulavr
make python
make build
ls ./build/pysimulavr/_pysimulavr.*.so

