from tika import parser
import re
import json
import sys
import utils


def get_load_number(content):
  match = re.compile(r'Load Confirmation\n(\d+)', re.MULTILINE).search(content)
  return match.group(1).strip() if match else None


def get_payer_info(content):
  return 'XPO Logistics'


def get_shipper_list(content):
  info = {}
  match = re.compile(r'^PU\s+(\d+/\d+/\d+)\n(\d+:\d+).*\n(?:[\d/:]+\n)*(.+\n)((?:.+\n)+?.*[A-Z]{2}\s\d{5})', re.MULTILINE).search(content)

  info['date'] = match.group(1).strip() if match else None
  info['time'] = match.group(2).strip() if match else None
  info['name'] = match.group(3).strip() if match else None
  info['address'] = match.group(4).strip() if match else None
  info['address'] = ', '.join(info['address'].splitlines()) if match else None

  return [info]


def get_receiver_list(content):
  info_list = []

  pattern = r'^SO\s+(\d+/\d+/\d+)\n(\d+:\d+).*\n(?:[\d/:]+\n)*(.+\n)((?:.+\n)+?.*[A-Z]{2}\s\d{5})'
  for match in re.finditer(pattern, content, re.MULTILINE):
    info = {}
    info['date'] = match.group(1).strip() if match else None
    info['time'] = match.group(2).strip() if match else None
    info['name'] = match.group(3).strip() if match else None
    info['address'] = match.group(4).strip() if match else None
    info['address'] = ', '.join(info['address'].splitlines()) if match else None

    info_list.append(info)

  return info_list


def get_total_charge(content):
  match = re.compile(r'Total Carrier Pay\s+\$(\d+\.?\d*)').search(content)
  return match.group(1).strip() if match else None

def has_signature(content):
  return re.compile(r'xpo.com').search(content)


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
