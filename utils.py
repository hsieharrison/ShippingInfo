from tika import parser
import subprocess
import json
import re
import os


def run_command(cmd, shell=True):
  """Structures for a variety of different test results.

  Args:
    cmd: Command to execute
    shell: True to use shell, false otherwise.

  Returns:
    Tuple of the command return value and the standard out in as a string.
  """
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, shell=shell)

  exit_code = None
  line = ''
  stdout = ''
  while exit_code is None or line:
    exit_code = p.poll()
    line = p.stdout.readline().decode('utf-8')
    stdout += line

  return exit_code, stdout


def read_data_from_file(path):
  with open(path, 'r') as file:
    content = file.read()
    content = json.loads(content)
    return content

def format_json(data):
  return json.dumps(data, indent=2, sort_keys=True, separators=(',', ': '))

def get_invoice_path(path):
  dirname = os.path.dirname(path)
  basename = os.path.basename(path)

  return os.path.join(dirname, 'invoice_{}'.format(basename))

def get_content(path):
  raw = parser.from_file(path, xmlContent=True)
  content = raw['content'].strip()
  content = content.replace('&amp;', '&')

  paragraphs = []
  for match in re.finditer('<p>((?:.*\n)*?)</p>', content):
    # Exclude paragraph which we are sure will not have the data we want
    if 'Please' in match.group(1):
      continue
    paragraphs.append(match.group(1))

  content = '\n'.join(paragraphs)
  lines = content.strip().splitlines()
  lines = [line.strip() for line in lines if len(line.strip())]
  content = '\n'.join(lines)

  return content




