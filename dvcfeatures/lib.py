import os
import subprocess
from contextlib import contextmanager

# Multilevel dictionary merge.
def merge(a, b, path=None):
    "merges b into a"
    if path is None:
        path = []
    for key in b:
        if ((key in a) and
            (isinstance(a[key], dict) and isinstance(b[key], dict))):
            merge(a[key], b[key], path + [str(key)])
        else:
            a[key] = b[key]

    return a


@contextmanager
def cwd(path):
    oldpwd=os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)

def run(cmd):

    print("[run]", " ".join(cmd))
    process = subprocess.Popen(cmd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    out, err = process.communicate()
    err = err.decode("utf-8")
    out = out.decode("utf-8")
    if len(out) > 0:
        print(out)
    if len(err) > 0: 
        print(err)

    return out
