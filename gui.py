import tkinter as tk
import tkinter.filedialog as filedialog
import parse_pdf
import os
import traceback
import tkinter.messagebox as messagebox
import json
from PIL import Image
import sys
import logging
import os
import argparse
import lib.google_sheets as google_sheets
import lib.utils as utils


def handle_exception(self, *args):
  error_message = ''.join(traceback.format_exception(*args))
  messagebox.showerror('Unexpected Exception', error_message)
  logging.error(error_message)


class GUI:
  def __init__(self, update_google_sheets):
    self.root = tk.Tk()
    self.root.title('Shipping Info Manager')
    self.update_google_sheets = update_google_sheets
    self.sheets = google_sheets.GoogleSheets() if update_google_sheets else None

    frame = tk.Frame(self.root, bd=3, relief='sunken')
    text = tk.Text(frame, width = 80, height=20, font=("arial", 16), wrap='none')
    scrollbar_x = tk.Scrollbar(frame, orient="horizontal", command=text.xview)
    scrollbar_y = tk.Scrollbar(frame, orient="vertical", command=text.yview)
    text['xscrollcommand'] = scrollbar_x.set
    text['yscrollcommand'] = scrollbar_y.set
    text.configure(state="disabled")
    text.bind("<1>", lambda event: text.focus_set())


    text.grid(row=0, column=0)
    scrollbar_y.grid(row=0, column=1, sticky='ns')
    scrollbar_x.grid(row=1, column=0, sticky='ew')

    generate_invoice_button = tk.Button(self.root, text="Generate Invoice",
                                        command=self.generate_invoice,
                                        font=('arial', 16, 'bold'))
    convert_pdf_button = tk.Button(self.root, text="Convert to PDF",
                                        command=self.convert_to_pdf,
                                        font=('arial', 16, 'bold'))

    frame.grid(row=0, rowspan=2, column=0, padx=10, pady=20)
    generate_invoice_button.grid(row=0, column=1, padx=5, pady=5)
    convert_pdf_button.grid(row=1, column=1, padx=5, pady=5)
    # text.insert(tk.END, 'a'*999 + '\n')

    self.text = text
    # self.root.geometry("1000x500")


  def append_message(self, message):
    self.text.configure(state="normal")
    self.text.insert(tk.END, message)
    self.text.configure(state="disabled")


  def convert_to_pdf(self):
    orig_path = filedialog.askopenfilename(
      initialdir=os.getcwd(), title='Select the rate confirmation pdf')    
    converted_path = os.path.splitext(orig_path)[0] + '.pdf'

    image = Image.open(orig_path)
    with open(converted_path, 'wb') as f:
      image.save(f, 'PDF')

    self.append_message('Successfully converted {} to {}\n'.format(
      orig_path, converted_path))


  def generate_invoice(self):
    path = filedialog.askopenfilename(
      initialdir=os.getcwd(), title='Select the rate confirmation pdf',
      filetypes = (('pdf files', '*.pdf'),('all files', '*.*')))

    if not path:
      return

    data = parse_pdf.parse_pdf(path)
    formatted_data = json.dumps(data, indent=2, sort_keys=True, separators=(',', ': '))
    self.append_message('File {} is parsed into data:\n{}\n'.format(path, formatted_data))

    invoice_path = utils.get_invoice_path(path)
    parse_pdf.generate_invoice(data, invoice_path)
    self.append_message('Successfully generated invoice at {}'.format(invoice_path))

    if self.update_google_sheets:
      row = google_sheets.get_row(data)
      self.sheets.append(row)
      self.append_message('Added row {} to Google sheets'.format(row))

  def start(self):
    self.root.mainloop()



if __name__ == "__main__":
  argument_parser = argparse.ArgumentParser(
    usage='parse_pdf.py <path_to_pdf> [<args>]',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  argument_parser.add_argument(
    '--update_google_sheets',
    action='store_true',
    help='If set, upload shipping info to Google Sheets'
    )

  FLAGS, unparsed = argument_parser.parse_known_args()

  fileHandler = logging.FileHandler("gui.log", mode='w')
  fileHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
  logging.getLogger().addHandler(fileHandler)

  consoleHandler = logging.StreamHandler()
  consoleHandler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
  logging.getLogger().addHandler(consoleHandler)

  logging.getLogger().setLevel(logging.DEBUG)

  if unparsed:
    logging.error('Arguments {} are not recognized'.format(unparsed))
    argument_parser.print_help()
    sys.exit(1)

  gui = GUI(FLAGS.update_google_sheets)
  tk.Tk.report_callback_exception = handle_exception
  gui.start()


