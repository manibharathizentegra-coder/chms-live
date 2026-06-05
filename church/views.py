# church/views.py
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from .services import get_zoho_records, get_teacher_records
from .services import get_student_records
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from .services import create_attendance_record
from .services import create_marks_record
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from .services import create_promote_record
from .services import create_promote_record, update_student_grade

def view_records(request):
    data = get_zoho_records("school-app", "Student_Report")
    return render(request, 'attendance/list.html', {'students': data})

def home(request):
    from .utils import getoauth
    token = getoauth()
    return HttpResponse(f"Refresh Token Success. Access Token: {token}")

def view_teachers(request):
    teachers = get_teacher_records()

    print("Teachers =", teachers)

    return render(
        request,
        "attendance/list.html",
        {"teachers": teachers}
    )

# church/views.py


def attendance_page(request):

    students = get_student_records()

    grades = []

    for student in students:

        grade = student.get("Class_Grade")

        if grade and grade not in grades:
            grades.append(grade)

    selected_grade = request.GET.get("grade")

    if selected_grade:

        students = [
            s for s in students
            if s.get("Class_Grade") == selected_grade
        ]

    context = {
        "students": students,
        "grades": grades,
        "selected_grade": selected_grade
    }

    return render(
        request,
        "attendance/attendance.html",
        context
    )

def view_students(request):

    students = get_student_records()

    grade = request.GET.get("grade")
    year = request.GET.get("year")

    if grade:
        students = [
            s for s in students
            if s.get("Class_Grade") == grade
        ]

    if year:
        students = [
            s for s in students
            if s.get("Academic_Year") == year
        ]

    academic_years = []

    for student in get_student_records():

        academic_year = student.get("Academic_Year")

        if academic_year and academic_year not in academic_years:
            academic_years.append(academic_year)

    return render(
        request,
        "attendance/student_list.html",
        {
            "students": students,
            "academic_years": academic_years
        }
    )

@csrf_exempt
def save_attendance(request):

    if request.method == "POST":

        body = json.loads(request.body)

        formatted_date = datetime.strptime(
            body["date"],
            "%Y-%m-%d"
        ).strftime("%d-%b-%Y")

        result = create_attendance_record({

            "Academic_Year": body["academic_year"],
            "Class_Grade": body["class_grade"],
            "Date_field": formatted_date,

            "Attendance_Details1": [

                {
                    "Student_name": body["student_name"],
                    "Attendance_details": body["status"]
                }

            ]

        })

        print("Zoho Result =", result)

        return JsonResponse(result)

    return JsonResponse(
        {"error": "POST only"},
        status=400
    )

def student_marks_page(request):

    students = get_student_records()

    academic_years = []

    for student in students:

        year = student.get("Academic_Year")

        if year and year not in academic_years:
            academic_years.append(year)

    return render(
        request,
        "attendance/student_marks.html",
        {
            "students": students,
            "academic_years": academic_years
        }
    )

@csrf_exempt
def save_marks(request):

    if request.method == "POST":

        body = json.loads(request.body)

        formatted_date = datetime.strptime(
            body["date"],
            "%Y-%m-%d"
        ).strftime("%d-%b-%Y")

        result = create_marks_record({

            "Academic_Year":
                body["academic_year"],

            "Class_Grade":
                body["class_grade"],

            "Exam_Name":
                body["exam_name"],

            "Date_field":
                formatted_date,

            "Mark_Details":
                body["mark_details"]

        })

        print(result)

        return JsonResponse(result)

    return JsonResponse(
        {"error": "POST only"},
        status=400
    )

@csrf_exempt
def send_grade_mail(request):

    if request.method == "POST":

        body = json.loads(request.body)

        grade = body["grade"]
        academic_year = body["academic_year"]

        subject = body["subject"]

        exam_date = body["exam_date"]
        exam_time = body["exam_time"]

        message = body["message"]

        final_message = f"""
Academic Year : {academic_year}

Grade : {grade}

Exam Date : {exam_date}

Exam Time : {exam_time}

{message}
"""

        students = get_student_records()

        email_list = []

        for student in students:

            if (
                student.get("Class_Grade") == grade
                and
                student.get("Academic_Year") == academic_year
            ):

                email = student.get("Student_Email")

                if email:
                    email_list.append(email)

        send_mail(
            subject,
            final_message,
            "manikandansjobzen@gmail.com",
            email_list,
            fail_silently=False
        )

        return JsonResponse({
            "count": len(email_list)
        })

    return JsonResponse({"error":"POST only"})

def send_mail_page(request):

    students = get_student_records()

    academic_years = []

    for student in students:

        year = student.get("Academic_Year")

        if year and year not in academic_years:
            academic_years.append(year)

    return render(
        request,
        "attendance/send_mail.html",
        {
            "academic_years": academic_years
        }
    )

def promote_students_page(request):

    students = get_student_records()

    academic_years = []

    for student in students:

        year = student.get("Academic_Year")

        if year and year not in academic_years:

            academic_years.append(year)

    return render(
        request,
        "attendance/promote_students.html",
        {
            "students": students,
            "academic_years": academic_years
        }
    )

@csrf_exempt
def save_promotion(request):

    if request.method != "POST":
        return JsonResponse(
            {"error": "POST only"},
            status=400
        )

    try:

        body = json.loads(request.body)

        formatted_date = datetime.now().strftime(
            "%d-%b-%Y"
        )

        result = create_promote_record({

            "Academic_Year":
                body.get("academic_year"),

            "Class_Grade":
                body.get("class_grade"),

            "Date_field":
                formatted_date,

            "Promote_Details": [

                {
                    "Student_Name":
                        body.get("student_name"),

                    "Current_Grade":
                        body.get("current_grade"),

                    "Promoted_To_Grade":
                        body.get("promoted_to_grade"),

                    "Promote_Status":
                        body.get("status")
                }

            ]
        })

        # Update student report grade
        if body.get("status") == "Promoted":

            update_student_grade(
                body.get("student_id"),
                body.get("promoted_to_grade")
            )

        return JsonResponse(result)

    except Exception as e:

        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )


        