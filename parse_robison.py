from tika import parser
import re
import json
import sys
import utils


def get_load_number(content):
  match = re.compile(r'Service for Load #(\d+)', re.MULTILINE).search(content)
  return match.group(1).strip() if match else None


def get_payer_info(content):
  match = re.compile(r'SUBMIT FREIGHT BILL TO.*\n((?:.+\n)*?)(.*[A-Z]{2}\s\d+)', re.MULTILINE).search(content)
  return ', '.join(''.join(match.group(1,2)).splitlines()) if match else None


def get_shipper_list(content):
  info = {}
  pattern = r'Ref #\n(.+\n)((?:.+\n)*?)(\d+/\d+/\d+)\n.*Pick.*\n(\d+:\d+)'
  match = re.compile(pattern, re.MULTILINE).search(content)

  info['name'] = match.group(1).strip() if match else None
  info['address'] = ', '.join(match.group(2).strip().splitlines()) if match else None
  info['date'] = match.group(3).strip() if match else None
  info['time'] = match.group(4).strip() if match else None

  return [info]


def get_receiver_list(content):
  info_list = []
  content_lines = [line.strip() for line in content.splitlines()]
  indexes = []
  for idx in range(len(content_lines)):
    if 'Ref #' in content_lines[idx]:
      indexes.append(idx)
  indexes.append(len(content_lines))

  for k in range(1, len(indexes) - 1):
    modified_content = '\n'.join(content_lines[indexes[k] : indexes[k + 1]])
    info = {}
    pattern = r'Ref #\n(.+\n)((?:.+\n)*?)((?:\d+/\d+/\d+\n)?)\*.*\*\n(\d+:\d+)'
    match = re.compile(pattern, re.MULTILINE).search(modified_content)

    if match:
      lines = '\n'.join(match.group(1, 2)).splitlines()
      lines = [line.strip() for line in lines if len(line.strip())]
      while len(lines) > 2 and not re.compile(r'^\d+\s').search(lines[1]):
        lines.pop(0)
      info['name'] = lines[0]
      info['address'] = ', '.join(lines[1:])
    else:
      info['name'] = None
      info['address'] = None
    info['date'] = match.group(3).strip() if match else None
    info['time'] = match.group(4).strip() if match else None
    info_list.append(info)

  return info_list


def get_total_charge(content):
  match = re.compile(r'^Total:\n(?:.*\n)*?\$([\d,\.]+)', re.MULTILINE).search(content)

  return match.group(1).replace(',', '') if match else None


def has_signature(content):
  return re.compile(r'Robinson').search(content)


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
