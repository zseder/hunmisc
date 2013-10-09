import io
import os
import subprocess
import tempfile

def gzip_open(filename):
    tmpdir = tempfile.mkdtemp()
    tmp_fifo = os.path.join(tmpdir, 'myfifo')

    os.mkfifo(tmp_fifo)

    p = subprocess.Popen("gzip --stdout -d %s > %s" % (filename, tmp_fifo), shell=True)
    f = io.open(tmp_fifo, "rb")

    while True:
        line = f.readline()
        yield line
        if not line: break
     
    f.close()
    p.wait()
     
    os.remove(tmp_fifo)
    os.rmdir(tmpdir)
