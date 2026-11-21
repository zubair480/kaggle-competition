"""Install g4edit.py as /tmp/g4edit.py for SEARCH/REPLACE edits through run_command."""
import os
import shutil
import subprocess

source = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'g4edit.py')
workspace = os.path.realpath(os.environ.get('PWD') or os.getcwd())
target = os.path.realpath(os.environ.get('TMPDIR') or '/tmp')


def inside_repository(path):
    if path == workspace or path.startswith(workspace + os.sep):
        return True
    try:
        return subprocess.run(['git', '-C', path, 'rev-parse', '--is-inside-work-tree'],
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.strip() == b'true'
    except Exception:
        return False


# The sandbox maps /tmp in run_command to $TMPDIR; never install into the repository,
# where the helper would become part of the patch.
if inside_repository(target):
    target = '/tmp'
os.makedirs(target, exist_ok=True)
destination = os.path.join(target, 'g4edit.py')
shutil.copyfile(source, destination)
os.chmod(destination, 0o755)
print("""INSTALLED /tmp/g4edit.py. Edit a source file with one run_command call:
python3 /tmp/g4edit.py path/to/file.py <<'EDIT'
<<<<<<< SEARCH
exact current lines (copied verbatim, with indentation)
=======
replacement lines
>>>>>>> REPLACE
EDIT""")
