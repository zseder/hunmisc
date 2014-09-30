import io
import os
import subprocess
import tempfile


def handle_subprocess_file(command_format_str):
    tmpdir = tempfile.mkdtemp()
    tmp_fifo = os.path.join(tmpdir, 'myfifo')

    os.mkfifo(tmp_fifo)

    p = subprocess.Popen(command_format_str.format(tmp_fifo), shell=True,
                         stderr=subprocess.PIPE)
    f = io.open(tmp_fifo, "rb")

    while True:
        line = f.readline()
        yield line
        if not line:
            break

    f.close()
    p.wait()

    os.remove(tmp_fifo)
    os.rmdir(tmpdir)


def gzip_open(filename):
    command = "gzip --stdout -d {0} > ".format(filename) + "{0}"
    for line in handle_subprocess_file(command):
        yield line


def l7zip_open(filename):
    command = "7zr x -so {0} > ".format(filename) + "{0}"
    for line in handle_subprocess_file(command):
        yield line


def bzip2_open(filename):
    command = "bunzip2 -c {0} > ".format(filename) + "{0}"
    for line in handle_subprocess_file(command):
        yield line
