from tika import parser
import re
import json
import sys
import argparse
import glob
import logging
import importlib
import traceback
import lib.utils as utils
import lib.google_sheets as google_sheets
from datetime import datetime
from os.path import dirname, basename, isfile, join


def is_valid(data):
  if not data:
    return False

  for value in data.values():
    if not value:
      return False

  return True


def add_missing_date_time(data):
  for info in data['shipper_list']:
    if 'date' not in info:
      info['date'] = ''
    if 'time' not in info:
      info['time'] = ''

  for info in data['receiver_list']:
    if 'date' not in info:
      info['date'] = ''
    if 'time' not in info:
      info['time'] = ''


def parse_pdf(path):
  content = utils.get_content(path)
  sys.path.append(join(dirname(__file__), 'lib'))
  files = glob.glob(join(join(dirname(__file__), 'lib'), "parse_*.py"))
  module_names = [ basename(file)[:-3] for file in files]

  for module_name in module_names:
    module = importlib.import_module('lib.{}'.format(module_name))
    try:
      data = getattr(module, 'get_data')(content)
    except Exception as e:
      print('Failed to parse data using {} due to exception:\n{}\n'.format(
          module_name, traceback.format_exc()))
      raise e
    if is_valid(data):
      print('Successfully parsed data using module {}'.format(module_name))
      add_missing_date_time(data)

      return data

  return None


def generate_invoice(data, path):
  from reportlab.pdfgen import canvas
  from reportlab.lib.pagesizes import letter, A4
  from reportlab.lib.units import inch
  from reportlab.lib.units import cm
  from reportlab.lib.enums import TA_LEFT
  from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
  from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

  text_lines = '<b>Invoice #</b>: {}\n<b>Invoice date</b>: {}\n<b>W/O (Ref)</b>: {}'.format(
    '0001', datetime.now().strftime('%Y-%m-%d'), data['load_number'])

  text_lines = '{}\n\n<b>BILL TO</b>:\n{}'.format(
    text_lines, data['payer_info'])

  shipper_idx = 0
  for shipper in data['shipper_list']:
    shipper_idx += 1
    text_lines = '{}\n\n<b>Shipper #</b>{}: {}\n<b>Address</b>: {}\n<b>Date</b>: {} {}'.format(
      text_lines, shipper_idx, shipper['name'], shipper['address'], shipper['date'], shipper['time'])

  receiver_idx = 0
  for receiver in data['receiver_list']:
    receiver_idx += 1
    text_lines = '{}\n\n<b>Receiver #</b>{}: {}\n<b>Address</b>: {}\n<b>Date</b>: {} {}'.format(
      text_lines, receiver_idx, receiver['name'], receiver['address'], receiver['date'], receiver['time'])

  text_lines = '{}\n\n<b>Total Rate</b>: ${}'.format(text_lines, data['total_charge'])

  styles=getSampleStyleSheet()
  styles.add(ParagraphStyle(name='Left', alignment=TA_LEFT))
  doc = SimpleDocTemplate(path, pagesize=A4,
                          rightMargin=2*cm, leftMargin=2*cm,
                          topMargin=2*cm, bottomMargin=2*cm)
  paragraphs = [Image(join(join(dirname(__file__), 'images'), 'logo.png'), 2.5 * cm, 2.5 * cm)]
  paragraphs.append(Spacer(1,0.2*inch))
  paragraphs.append(Paragraph(text_lines.replace("\n", "<br />"), styles['Normal']))
  doc.build(paragraphs)

  # textobject.setFont("Courier", 10)

  print('Successfully generated invoice {}'.format(path))



if __name__ == "__main__":
  argument_parser = argparse.ArgumentParser(
    usage='parse_pdf.py <path_to_pdf> [<args>]',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  argument_parser.add_argument(
    'path', type=str, help='Path to the pdf file')
  argument_parser.add_argument(
    '--update_google_sheets',
    action='store_true',
    help='If set, upload shipping info to Google Sheets'
    )
  argument_parser.add_argument(
    '--generate_invoice_pdf',
    action='store_true',
    help='If set, generate invoice pdf'
    )


  FLAGS, unparsed = argument_parser.parse_known_args()

  if unparsed:
    print('Arguments {} are not recognized'.format(unparsed))
    argument_parser.print_help()
    sys.exit(1)

  data = parse_pdf(FLAGS.path)
  print('data is: {}\n'.format(json.dumps(data, indent=2, sort_keys=True, separators=(',', ': '))))

  if FLAGS.generate_invoice_pdf:
    generate_invoice(data, utils.get_invoice_path(FLAGS.path))

  if FLAGS.update_google_sheets:
    sheets = google_sheets.GoogleSheets()
    row = google_sheets.get_row(data)
    sheets.append(row)
    print('Added row {} to Google sheets'.format(row))

