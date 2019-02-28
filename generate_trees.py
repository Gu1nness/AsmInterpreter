import os
import sys
path = '/home/remi/Travaux_ENS/Stage_FZN/c_asm_memcheck/fibo'

def process_file(file_name):
    real_path = os.path.join(path, file_name)
    print("PROCESSING %s ..." % real_path)
    input_filename = "{}.c".format(real_path)
    dot_filename = "{}.dot".format(real_path)
    png_filename = "{}.png".format(real_path)

    os.system('python genastdot.py {} > {} && dot -Tpng -o {} {}'.format(
        input_filename,
        dot_filename,
        png_filename,
        dot_filename,
    ))
    # break
    print("FINISHED %s" % real_path)

if len(sys.argv) >= 2:
    print(sys.argv)
    for i in sys.argv[1:]:
        process_file(i)
else:
    filename = 'fibo'
    process_file(filename)


