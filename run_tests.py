from __future__ import print_function

import sys
import os
import json
import tika.parser as parser
import glob
from os.path import dirname, basename, isfile, join
import os
import lib.utils as utils
import parse_pdf


if __name__ == "__main__":
    path = sys.argv[1]  #D:\Projects\Harrisons Pjt\shipping_info_manager-master\PDFs
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames: # filenames = ['1.pdf', '1.txt'] | filename = '1.pdf'
            if not filename.endswith('.pdf'):
                continue
            pdf_file = join(dirpath, filename) # D:\Projects\Harrisons Pjt\shipping_info_manager-master\PDFs + 1.pdf
            text_file = join(dirpath, filename[:-3]+'txt') #D:\Projects\Harrisons Pjt\shipping_info_manager-master\PDFs + 1. + txt
            
            if not os.path.exists(text_file):
                continue
                
            data = parse_pdf.parse_pdf(pdf_file)
            expected_data = utils.read_data_from_file(text_file)
            
            if expected_data != data:
                print('The content bewtween {} and {} is inconsistent'.format(pdf_file, text_file))
                print('Expected data is:\n{}'.format(utils.format_json(expected_data)))
                print('Data generated from pdf is:\n{}'.format(utils.format_json(data)))
                sys.exit(1)
    print('All tests have passed.')
