from tika import parser
import re
import json
import sys
import utils



def get_load_number(content):
    match = re.compile(r'LOAD #: (\d+)').search(content)
    return match.group(1).strip() if match else None
def get_payer_info(content):
    match = re.compile(r'(RYAN TRANSPORTATION SERVICE, INC)').search(content)
    return match.group(1).strip() if match else None
def get_total_charge(content):
    match = re.compile(r'Total Carrier Pay: \$((\d+,?)+\.?\d*)').search(content)
    return match.group(1).strip() if match else None
def has_signature(content):
    return re.compile(r'RYAN TRANSPORTATION SERVICE, INC').search(content)

#----------------------------------------------------
def get_shipper_list(content):
    if not re.compile(r'SO\d+').search(content):
        return []

    match = re.compile(r'PU\d+ ((.*\n)*?)_').search(content).group(1).strip()
    return get_x_list(match)

def get_receiver_list(content):
    match = re.compile(r'SO\d+ ((.*\n)*?)_').search(content).group(1).strip()
    return get_x_list(match)

def get_x_list(match):
    match = match.replace('\n'," ")
    match = re.sub(' +', ' ', match)
    info = {}
    info['date'] = re.compile(r'Date: (\d{1,2}\/\d{1,2}\/\d{2,4})').search(match).group(1).strip() if match else None
    info['time'] = re.compile(r'Date: \d{1,2}\/\d{1,2}\/\d{2,4} (\d{4})').search(match).group(1).strip() if match else None
    info['name'] = re.compile(r'Name: (.*?) Date: \d').search(match).group(1).strip() if match else None
    info['address'] = re.compile(r'Address: (.*) Contact:').search(match).group(1).strip() if match else None
    info['address'] = re.sub(r'\d{1,2}\/\d{1,2}\/\d{2,4} \d{4} ', "", info['address'])
    info_list = []
    info_list.append(info)
    return info_list


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