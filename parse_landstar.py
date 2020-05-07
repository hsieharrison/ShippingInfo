from tika import parser
import re
import json
import sys
import utils


def get_load_number(content):
  match = re.compile(r'^CMX\n(\d+)$', re.MULTILINE).search(content)
  return match.group(1).strip() if match else None


def get_payer_info(content):
  match = re.compile(r'LANDSTAR EXPRESS AMERICA, INC', re.MULTILINE).search(content)
  return match.group(0) if match else None


def get_shipper_list(content):
  info = {}

  # Add pattern for name and address, where address lines possibly interleave with phone and contact
  pattern = r'^\d+\n^\d+\n(.+\n)((?:.+\n)+)(^.*\s?[A-Z]{2}\s\d{5}$)\n'
  # Add pattern for date and time
  pattern += r'(?:.+\n)+(\d{2}/\d{2}/\d{4})\s+(\d+:\d+)'

  match = re.compile(pattern, re.MULTILINE).search(content)

  info['name'] = match.group(1).strip() if match else None
  if match:
    address_lines = match.group(2).splitlines()
    # NOTE: we assume that phone number is specified iff contact is specified
    if len(address_lines) > 2 and re.compile('^\d+$').search(address_lines[-2]):
      address_lines = address_lines[:-2]
    address_lines.append(match.group(3).strip())
    info['address'] = ', '.join(address_lines)
  else:
    info['address'] = None
  info['date'] = match.group(4).strip() if match else None
  info['time'] = match.group(5).strip() if match else None

  return [info]


def get_receiver_list(content):
  info = {}

  # Add pattern for shipper name and shipper address, where shipper address
  # lines possibly interleave with phone and contact
  pattern = r'^\d+\n^\d+\n(.+\n)((?:.+\n)+)(^.*\s?[A-Z]{2}\s\d{5}$)\n'
  # Add pattern for receiver name and receiver address.
  pattern += r'(.+\n)((?:.+\n)+)'
  # Add pattern for date and time
  pattern += r'(\d{2}/\d{2}/\d{4})\s+(\d+:\d+)'

  match = re.compile(pattern, re.MULTILINE).search(content)

  info['name'] = match.group(4).strip() if match else None
  info['address'] = ', '.join(match.group(5).splitlines()) if match else None

  return [info]

def get_total_charge(content):
  lines = content.splitlines()
  while len(lines) and lines[0] != 'CMX':
    lines.pop(0)
  lines = lines[2:]
  while len(lines) > 1 and re.compile(r'\d+,?\.\d+').search(lines[1]):
    lines.pop(0)

  return lines[0].replace(',', '') if len(lines) else None


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
