from flask import Flask, request, jsonify, render_template_string
import json
import csv

app = Flask(__name__)

# Path to the CSV file
csv_file_path = 'detailed_participants.csv'

def load_participants():
    """Load participants from the CSV file."""
    global participants
    participants = {}
    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            participants[row["ID"]] = {
                "Name": row["Name"],
                "Email": row["Email"],
                "Phone Number": row["Phone Number"],
                "Affiliation": row["Affiliation"],
                "Role": row["Role"],
                "Ticket Type": row["Ticket Type"],
                "Checked In": row["Checked In"] == 'True'
            }

def update_csv():
    """Update the CSV file with the current participant data."""
    with open(csv_file_path, mode='w', newline='') as file:
        fieldnames = ["ID", "Name", "Email", "Phone Number", "Affiliation", "Role", "Ticket Type", "Checked In"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for pid, details in participants.items():
            row = details.copy()
            row["ID"] = pid
            row["Checked In"] = 'True' if row["Checked In"] else 'False'
            writer.writerow(row)

# Load participants initially
load_participants()

# HTML template for QR code scanning and displaying details
html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>TEDx Event Check-In</title>
    <script src="https://cdn.jsdelivr.net/npm/html5-qrcode/minified/html5-qrcode.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: row;
            align-items: flex-start;
            padding: 20px;
        }
        #reader {
            width: 500px;
            height: 500px;
            border: 1px solid #ddd;
        }
        #details {
            margin-left: 20px;
            flex: 1;
        }
        #details h2 {
            margin-top: 0;
        }
    </style>
</head>
<body>
    <div id="reader"></div>
    <div id="details"></div>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Handle the scanned result
            fetch(`/check-in?data=${encodeURIComponent(decodedText)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('details').innerHTML = `
                            <h2>Participant Details</h2>
                            <p>ID: ${data.details.ID}</p>
                            <p>Name: ${data.details.Name}</p>
                            <p>Email: ${data.details.Email}</p>
                            <p>Phone Number: ${data.details["Phone Number"]}</p>
                            <p>Affiliation: ${data.details.Affiliation}</p>
                            <p>Role: ${data.details.Role}</p>
                            <p>Ticket Type: ${data.details["Ticket Type"]}</p>
                            <p>Status: ${data.details["Checked In"] ? "Checked In" : "Not Checked In"}</p>
                        `;
                    } else {
                        document.getElementById('details').innerHTML = '<p>Check-in failed. Invalid QR code.</p>';
                    }
                });
        }

        let html5QrcodeScanner = new Html5QrcodeScanner(
            "reader", { fps: 10, qrbox: 250 }, false);
        html5QrcodeScanner.render(onScanSuccess);

        // Check if the library was loaded
        if (!window.Html5QrcodeScanner) {
            console.error('Html5QrcodeScanner library is not loaded');
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/check-in', methods=['GET'])
def check_in():
    qr_data = request.args.get('data')
    try:
        participant_details = json.loads(qr_data)
        participant_id = participant_details["ID"]
        if participant_id in participants:
            participants[participant_id]["Checked In"] = True
            update_csv()  # Update the CSV file
            return jsonify(success=True, details=participants[participant_id])
        else:
            return jsonify(success=False)
    except json.JSONDecodeError:
        return jsonify(success=False)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change the port to 5001
