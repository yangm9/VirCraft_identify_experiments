#!/bin/bash
cp 2.subsampling_after_fragment_train.py train && python 2.subsampling_after_fragment_train.py
cp 2.subsampling_after_fragment_val.py val && python 2.subsampling_after_fragment_val.py
cp 2.subsampling_after_fragment_test.py test && python 2.subsampling_after_fragment_test.py

