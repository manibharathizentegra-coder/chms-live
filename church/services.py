# church/services.py
import requests
from .utils import getoauth

def get_headers():
    return {"Authorization": f"Zoho-oauthtoken {getoauth()}", "Content-Type": "application/json"}

def get_zoho_records(app_link, report_link):
    url = f"https://creator.zoho.in/api/v2.1/zentegraindia/{app_link}/report/{report_link}"
    response = requests.get(url, headers=get_headers())
    return response.json().get('data', []) if response.status_code == 200 else []

def get_teacher_records():
    url = "https://creator.zoho.in/api/v2.1/zentegraindia/chms/report/Add_Teacher_Report"

    response = requests.get(url, headers=get_headers())

    return response.json().get("data", [])

def get_student_records():
    url = "https://creator.zoho.in/api/v2.1/zentegraindia/chms/report/Add_Student_Report"

    response = requests.get(
        url,
        headers=get_headers()
    )

    data = response.json().get("data", [])

    print(data)   # <-- Add this

    return data


def create_attendance_record(data):

    url = "https://creator.zoho.in/api/v2.1/zentegraindia/chms/form/Student_Attendance"

    payload = {
        "data": data
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Zoho-oauthtoken {getoauth()}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    return response.json()

def create_marks_record(data):

    url = "https://creator.zoho.in/api/v2.1/zentegraindia/chms/form/Student_Marks"

    payload = {
        "data": data
    }

    response = requests.post(
        url,
        headers=get_headers(),
        json=payload
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    return response.json()

def create_promote_record(data):

    url = "https://creator.zoho.in/api/v2.1/zentegraindia/chms/form/Student_Promote_Details"

    payload = {
        "data": data
    }

    response = requests.post(
        url,
        headers=get_headers(),
        json=payload
    )

    print("Status:", response.status_code)
    print("Response:", response.text)

    return response.json()

def update_student_grade(record_id, new_grade):

    url = (
        f"https://creator.zoho.in/api/v2.1/"
        f"zentegraindia/chms/report/"
        f"Add_Student_Report/{record_id}"
    )

    payload = {
        "data": {
            "Class_Grade": new_grade
        }
    }

    response = requests.patch(
        url,
        headers=get_headers(),
        json=payload
    )

    print("UPDATE STATUS:", response.status_code)
    print("UPDATE RESPONSE:", response.text)

    return response.json()
