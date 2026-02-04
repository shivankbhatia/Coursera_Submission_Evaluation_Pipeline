import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading

# Thread safety lock
sheet_lock = threading.Lock()

# -------------------------
# AUTHENTICATION
# -------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)

# -------------------------
# OPEN SHEET
# -------------------------
sheet = client.open("Evaluation_Live_Output").sheet1


# -------------------------
# INITIALIZE HEADERS
# -------------------------
def init_sheet():

    headers = [
        "Roll Number",
        "Full Name",
        "Coursera Project",
        "Certificate Completion Date",
        "Project Mention Match",
        "Final Verdict",
        "Failure Reason"
    ]

    existing = sheet.row_values(1)

    if existing != headers:
        sheet.clear()
        sheet.append_row(headers)
        print("✅ Google Sheet headers initialized")
    else:
        print("ℹ️ Google Sheet headers already present")


# -------------------------
# APPEND LIVE ROW
# -------------------------
def append_result_live(row_data):

    with sheet_lock:
        sheet.append_row(row_data)
