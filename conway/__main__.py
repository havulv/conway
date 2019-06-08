#! /usr/bin/env python3.7

from . import strife
import sys


if __name__ == "__main__":
    strife.main(strife.parse_args(sys.argv[1:]))
