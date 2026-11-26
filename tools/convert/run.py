"""rebuild the tile databases, the extra tileset rows and every World 3 to 8 map"""
import glob, os, runpy, sys
from paths import HERE

os.chdir(HERE)
sys.path.insert(0, HERE)
for script in ['db.py', 'addtiles.py', 'fixflags.py', 'world12.py'] + sorted(glob.glob('gen[0-9][0-9].py')) + ['bowsers.py']:
    print('--', script)
    runpy.run_path(script, run_name='__main__')
