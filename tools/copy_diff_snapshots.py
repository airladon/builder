import sys
sys.path.insert(0, './app/app')
from copy_diff_snapshots import copy_diff_snapshots    # noqa

copy_path = './logs/temp'
if len(sys.argv) > 1:
    copy_path = sys.argv[1]

copy_diff_snapshots(copy_path)
