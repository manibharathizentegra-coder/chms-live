# church/services.py
import requests
from .utils import IntiateOauth

def get_headers():

    token = IntiateOauth()

    if not token:
        raise Exception(
            "Unable to generate Zoho access token"
        )

    return {
        "Authorization": f"Zoho-oauthtoken {token}",
        "Content-Type": "application/json"
    }

def get_zoho_records(app_link, report_link):
    url = f"https://creator.zoho.in/api/v2.1/zentegraindia/{app_link}/report/{report_link}"
    response = requests.get(url, headers=get_headers())
    return response.json().get('data', []) if response.status_code == 200 else []

def get_teacher_records():
    url = "https://creator.zoho.in/api/v2.1/zentegraindia/chms/report/Add_Teacher_Report"
    headers = get_headers()
    response = requests.get(url, headers=headers)
    print("response - ",headers)
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
        headers=get_headers(),
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
    print("payload :", payload)

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

def teacher_email_exists(email):

    teachers = get_teacher_records()

    for teacher in teachers:

        teacher_email = teacher.get("Email1")

        if teacher_email and teacher_email.lower() == email.lower():
            return True

    return False

def get_teacher_by_email(email):

    teachers = get_teacher_records()

    for teacher in teachers:

        teacher_email = teacher.get("Email1")

        if (
            teacher_email
            and
            teacher_email.lower() == email.lower()
        ):
            print("MATCHED TEACHER =", teacher)
            return teacher

    print("NO TEACHER FOUND FOR =", email)

    return None

def get_teacher_grade_assignments():
    url = "https://creator.zoho.in/api/v2.1/zentegraindia/chms/report/Assign_Grade_To_Teacher_Report"

    response = requests.get(
        url,
        headers=get_headers()
    )

    return response.json().get("data", [])

def get_attendance_records():
    return get_zoho_records(
        "chms",
        "Student_Attendance_Report"
    )

def get_grade_assignments():
    return get_zoho_records(
        "chms",
        "Assign_Grade_To_Teacher_Report"
    )

def get_schedule_class_records():

    url = (
        "https://creator.zoho.in/api/v2.1/zentegraindia/chms/report/Schedule_Class_To_Teacher_Report"
    )

    response = requests.get(
        url,
        headers=get_headers()
    )

    print("STATUS =", response.status_code)
    print("RESPONSE =", response.text)

    return response.json().get("data", [])

def get_teacher_students(email):

    teacher = get_teacher_by_email(email)

    if not teacher:
        return []

    teacher_id = str(teacher.get("ID"))

    assignments = get_schedule_class_records()

    students = get_student_records()

    my_students = []

    for assignment in assignments:

        teacher_lookup = assignment.get("Select_Teacher", {})

        assigned_teacher_id = str(
            teacher_lookup.get("ID", "")
        )

        if assigned_teacher_id != teacher_id:
            continue

        assignment_year = (
            assignment.get(
                "Select_Academic_Year",
                {}
            ).get(
                "Academic_Year",
                ""
            )
        )

        grade_name = (
            assignment.get(
                "Select_Grade",
                {}
            ).get(
                "Grade_name",
                ""
            )
        )

        for student in students:

            if (
                student.get("Class_Grade") == grade_name
                and
                student.get("Academic_Year") == assignment_year
            ):
                my_students.append(student)

    return my_students
