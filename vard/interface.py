import os
from subprocess import *
from django.conf import settings

def jarWrapper(*args):
    process = Popen(['java', '-Xms8G', '-jar']+list(args), stdout=PIPE, stderr=PIPE)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith('\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split('\n')
    if stderr != '':
        ret += stderr.split('\n')
    ret.remove('')
    return ret

BASE_DIR = settings.BASE_DIR
#programs args
jar_file = BASE_DIR + '/vard/vard_source/1clui.jar'
in_file_test = BASE_DIR + '/test_book.txt'
setup_folder = BASE_DIR + '/vard/vard_source'
threshold_int = '30'
f_score = '1'
input_file = ''
output_type = 'Plain'
output_file_dir = BASE_DIR + '/vard/vard_resource/'
memory_arg = '-Xms2G -Xmx4G'

def do_vard(doc_text, vard_options):
    """
    runs a text file through vard for spelling normalization
    :param input_file:
    :return:
    """
    output_file = output_file_dir + 'the_output.txt'
    open(os.path.dirname(os.path.realpath(__file__)) + '/vard_resource/input_file.txt', 'w').close()

    with open(os.path.dirname(os.path.realpath(__file__)) + '/vard_resource/input_file.txt', 'w') as f:
        f.write(doc_text)
        f.close()

    input_file_path = os.path.dirname(os.path.realpath(__file__)) + '/vard_resource/input_file.txt'
    threshold_int = vard_options['threshold']
    f_score = vard_options['fScore']

    args = [jar_file, setup_folder, threshold_int, f_score, input_file_path, output_type, output_file]

    #delete_any_possible_current_output_files
    try:
        os.remove(output_file)
    except Exception:
        pass
    #create an empty output file
    open(output_file, 'w').close()
    #run the process
    result = jarWrapper(*args)

    with open(output_file, 'rb') as f:
        finished = f.read()
        f.close()
    #remove the file
    os.remove(output_file)
    os.remove(input_file_path)
    print 'done with VARD2 task'
    return finished









