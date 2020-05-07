from tika import parser
import re
import json
import sys
import utils


def get_load_number(content):
  match = re.compile(r'LOAD NUMBER (\d+)').search(content)
  return match.group(1).strip() if match else None

def get_payer_info(content):
  return "Sunteck Transport Co." if re.compile(r'Sunteck').search(content) else None

def get_shipper_list(content):
    if not re.compile(r'PICKUP \d{1,2}\/').search(content):
        return []

    document = content.splitlines()
    return get_x_list(document, r'^PICKUP \d{1,2}\/')

def get_receiver_list(content):
    if not re.compile(r'DELIVER \d{1,2}\/').search(content):
        return []

    document = content.splitlines()
    return get_x_list(document, r'^DELIVER \d{1,2}\/')

def get_x_list(document, x):
    index = 0

    match = re.compile(x).search(document[index])
    while index + 1 < len(document) and not match:
        index += 1
        match = re.compile(x).search(document[index])

    info = {}
    info['date'] = re.compile(r'(\d{1,2}\/\d{1,2}\/\d{4})').search(document[index]).group(1).strip() if match else None
    try:
        info['time'] = re.compile(r'(\d{2}:\d{2})').search(document[index]).group(1).strip()
    except AttributeError:
        info['time'] = "N/A"
    info['name'] = document[index + 1] if match else None
    info['address'] = document[index+2] + ", " + document[index+3] if match else None
    info_list = []
    info_list.append(info)
    return info_list

def get_total_charge(content):
  match = re.compile(r'\$(\d+(\,?\d{3})*\.?\d{0,2})').search(content)
  return match.group(1).strip() if match else None

def has_signature(content):
  return re.compile(r'Sunteck').search(content)

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
