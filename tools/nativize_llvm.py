#!/usr/bin/env python2
"""Small utility to build some llvm bitcode into native code. Useful when lli
(called from exec_llvm) fails for some reason.

 * Use llc to generate x86 asm
 * Use as to generate an object file
 * Use g++ to link it to an executable
"""

from __future__ import print_function
import os, sys
from subprocess import call, check_call, PIPE, STDOUT

sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.shared import *

__rootpath__ = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
def path_from_root(*pathelems):
  return os.path.join(__rootpath__, *pathelems)

filename = sys.argv[1]
libs = sys.argv[2:] # e.g.: dl for dlopen/dlclose, util for openpty/forkpty

print('bc => clean bc')
check_call([LLVM_OPT, filename, '-strip-debug', '-o', filename + '.clean.bc'])
print('bc => s')
for params in [['-march=x86'], ['-march=x86-64']]: # try x86, then x86-64 FIXME
  print('params', params)
  for triple in [['-mtriple=i386-pc-linux-gnu'], []]:
    call([LLVM_COMPILER] + params + triple + [filename + '.clean.bc', '-o', filename + '.s'])
    print('s => o')
    call(['as', filename + '.s', '-o', filename + '.o'])
    if os.path.exists(filename + '.o'): break
  if os.path.exists(filename + '.o'): break

if not os.path.exists(filename + '.o'):
  print('tools/nativize_llvm.py: Failed to convert "' + filename + '" to "' + filename + '.o"!', file=sys.stderr)
  sys.exit(1)

print('o => runnable')
check_call(['g++', path_from_root('system', 'lib', 'debugging.cpp'), filename + '.o', '-o', filename + '.run'] + ['-l' + lib for lib in libs])

sys.exit(0)
