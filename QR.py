import os
import csv
import qrcode
import json

# Create directory for QR codes if it does not exist
qr_codes_dir = 'qr_codes'
os.makedirs(qr_codes_dir, exist_ok=True)

# Path to the CSV file
csv_file_path = 'detailed_participants.csv'

# Generate and save QR codes with all details
with open(csv_file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        participant_details = {
            "ID": row["ID"],
            "Name": row["Name"],
            "Email": row["Email"],
            "Phone Number": row["Phone Number"],
            "Affiliation": row["Affiliation"],
            "Role": row["Role"],
            "Ticket Type": row["Ticket Type"]
        }
        qr_data = json.dumps(participant_details)
        qr = qrcode.make(qr_data)
        qr.save(f'{qr_codes_dir}/{row["ID"]}.png')

print("QR codes generated and saved in the 'qr_codes' directory.")
