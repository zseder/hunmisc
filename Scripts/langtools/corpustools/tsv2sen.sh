#!/bin/sh
sed 's/^$/@/g' | tr '\n' ' ' | sed 's/ @ /\n/g' | tr '\t' '|'
