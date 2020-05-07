from __future__ import print_function

import sys
import tika.parser as parser
import os
import json
from os.path import join, isfile

import lib.utils as utils
import parse_pdf


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print('Usage: {} path_to_directory'.format(sys.argv[0]))
    sys.exit(1)

  path = sys.argv[1]
  for (dirpath, dirnames, filenames) in os.walk(path):
    for filename in filenames:
      if not filename.endswith('.pdf'):
        continue
      pdf_file = join(dirpath, filename)
      text_file = join(dirpath, filename[:-3]+'txt')

      print('file is {}'.format(pdf_file))
      data = parse_pdf.parse_pdf(pdf_file)
      with open(text_file, 'w') as f:
        print(json.dumps(data, indent=2, sort_keys=True, separators=(',', ': ')), file=f)


