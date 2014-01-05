from glob import glob
import os

from iterview import iterview


for filename in iterview(glob('data/cache/html/*/*'), inc=1000):
    try:
        with file(filename) as f:
            contents = f.read()
            assert contents
            assert '<title>Off-Campus' not in contents
    except AssertionError:
        print 'Removing ', filename
        os.remove(filename)
