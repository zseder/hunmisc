#!/bin/sh
sed 's/$/@/g'  | tr ' @' '\n'  | tr '|' '\t'
