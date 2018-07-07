import sys

fname = sys.argv[1]
rf = open(fname, 'r')
af = open(fname+'.tmp', 'w')

# Consume the first line which is assumed to be the first line of the target file
#next(rf)

shd_move = False
for line in rf:
    
    # Allow C or Java style comments
    if line.startswith('//'):
        line = '#' + line[2:]
        shd_move = True

    #(If a print statement if written in Python 2 style without parentheses)
    # wrap it in parentheses, then run the file.
    if 'print' in line and ' ' == line[line.index('print')+len('print')]:
        # Say that it is Python 2 style if there a space right after `print`
        # in the line. Could be edge cases that don't work that I'm not aware of.
        shd_move = True

        # Sometimes VS Code uses spaces instead of tabs, so basically consume
        # whitespace.
        s = 0
        while line[s] == ' ' or line[s] == '\t':
            s += 1

        i = line[s:].index(' ')+s
        line = line[:i] + '(' + line[i+1:-1] + ')\n'

    af.write(line)


import os

# If we changed a line in the file, <file>.tmp is different and we want to move
# it to <file>.
if shd_move:
    os.rename(fname+'.tmp', fname)
    
# Otherwise, just delete it.
else:
    os.remove(fname+'.tmp')
    
rf.close()
af.close()
    
# Run the actual file with changes.
import subprocess
subprocess.call(['python', fname] + sys.argv[2:])