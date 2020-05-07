from tika import parser
import re
import json
import sys
import utils


def get_load_number(content):
  match = re.compile(r'^FB #: (\d+)', re.MULTILINE).search(content)
  return match.group(1).strip() if match else None


def get_payer_info(content):
  match = re.compile(r'LANDSTAR RANGER', re.MULTILINE).search(content)
  return match.group(0) if match else None


def get_shipper_list(content):
  info = {}

  pattern = r'PICK-UP.*?(\d+/\d+/\d+)\s(\d+:\d+).*\n'
  pattern += r'NAME/ADDRESS:\s(.*)\s(\d+.*)PHONE:.*\n((?:.*\n)*?)DIRECTIONS:'

  match = re.compile(pattern, re.MULTILINE).search(content)

  info['date'] = match.group(1) if match else None
  info['time'] = match.group(2) if match else None
  info['name'] = match.group(3).strip() if match else None
  info['address'] = match.group(4).strip() if match else None
  if match:
    for line in match.group(5).splitlines():
      if re.compile(r'[a-zA-Z]+,\s[A-Z]{2}').match(line):
        info['address'] = '{}, {}'.format(info['address'], line)

  return [info]


def get_receiver_list(content):
  info = {}

  pattern = r'DELIVERY.*?(\d+/\d+/\d+)\s(\d+:\d+).*\n'
  pattern += r'NAME/ADDRESS:\s(.*)\s(\d+.*)PHONE:.*\n((?:.*\n)*?)DIRECTIONS:'

  match = re.compile(pattern, re.MULTILINE).search(content)

  info['date'] = match.group(1) if match else None
  info['time'] = match.group(2) if match else None
  info['name'] = match.group(3).strip() if match else None
  info['address'] = match.group(4).strip() if match else None
  if match:
    for line in match.group(5).splitlines():
      if re.compile(r'[a-zA-Z]+,\s[A-Z]{2}').match(line):
        info['address'] = '{}, {}'.format(info['address'], line)

  return [info]


def get_total_charge(content):
  match = re.compile(r'Total Carrier Pay:\s+\$([\d,\.]+)').search(content)

  return match.group(1) if match else None


def has_signature(content):
  return re.compile(r'Landstar', re.IGNORECASE).search(content)


def get_data(content):
  if not has_signature(content):
    return None

  data = {}
  data['load_number'] = get_load_number(content)
  data['payer_info'] = get_payer_info(content)
  data['shipper_list'] = get_shipper_list(content)
  data['receiver_list'] = get_receiver_list(content)
  data['total_charge'] = get_total_charge(content)

  return data


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print('Usage: {} path_to_pdf'.format(sys.argv[0]))
    sys.exit(1)

  path = sys.argv[1]
  content = utils.get_content(path)
  data = get_data(content)

  print('\ndata is: {}\n'.format(json.dumps(data, indent=2, sort_keys=True, separators=(',', ': '))))
