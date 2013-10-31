wget "http://www.csie.ntu.edu.tw/~cjlin/cgi-bin/liblinear.cgi?+http://www.csie.ntu.edu.tw/~cjlin/liblinear+tar.gz"
mv liblinear*gz liblinear.tar.gz
tar xzvf liblinear.tar.gz
mv liblinear-* liblinear
cd liblinear
make
cd python
patch < ../../liblinear.patch
make
mv *py ../../
