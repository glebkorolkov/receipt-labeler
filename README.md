# Receipt labeler

### Background

One could use [Google Cloud Vision](https://cloud.google.com/vision/) API to do optical character recognition (OCR) on images of receipts. Resulting text data could then be used to build a machine-learning model identifying various receipt metrics such as total amount, merchant name or receipt date.

In the previous project [Receipt Parser](https://github.com/glebkorolkov/receipt-parser) I parsed data coming out of OCR to extract meaningful information about receipt words such as text and location. My objective for this project was to build a visualization and labeling tool. I am planning to use it to manually label certain receipt words as 'Total amount', 'Sub-total', 'Tax', 'Merchant' or 'Date' and then build a machine learning model for identification of these metrics on a receipt.

### General information

The app is a Django-based web site. It uses MySQL database and D3.js on the front-end for visualization.

### Installation

The app can be installed and run like any other Django web site. Follow these steps on Unix-like operating systems:

1. Clone the repository into any folder and cd into the folder containing `requirements.txt`
2. Create virtual environment `python -m venv venv`, activate it `source venv/bin/activate` and install dependencies `pip install -r requirements.txt`
3. Set up a MySQL database server, create database 'receipt_labeler', configure database credentials in `app/app/settings.py`
4. Navigate to folder containing `manage.py` and run `python manage.py makemigrations` and then `python manage.py migrate`. This will create tables in the database
5. Run `python manage.py createsuperuser` and enter admin user's username, email and password
6. Download csv files with sample data: [receipts.csv](https://s3.amazonaws.com/receipt-labeler/csv/receipts.csv) and [words.csv](https://s3.amazonaws.com/receipt-labeler/csv/words.csv). Import them into the database using `load_data.sql` script in this repository's root
7. Navigate to folder containing `manage.py` and run `python manage.py runserver`. The app should now be up and running. You will need to log in with admin credentials

A working version of the app is available here: http://ec2-107-21-148-237.compute-1.amazonaws.com:8888/labeler/. Use username `guest` and password `guestguest` to authenticate.

### Usage

The main page lists all receipts in the database and shows which ones have already been labeled. You can click on any receipt to see its details. On the receipt view page will see the reconstructed receipt. You can click on individual receipt words and assign them as receipt labels. To view the actual receipt image press the 'Image' button.

### Next steps

I am planning to build a machine-learning based model for the identification of receipt metrics using labeled data obtained with this tool.