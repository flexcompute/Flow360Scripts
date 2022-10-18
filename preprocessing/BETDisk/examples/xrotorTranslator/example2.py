
# the below import will not work without python setup.py install or python setup.py develop
import sys
print(sys.path)

try:
    import preprocessing.BETDisk
except ImportError:
    print('cannot import preprocessing.BETDisks')    



try:
    import BETDisk
except ImportError:
    print('cannot import BETDisks')    

