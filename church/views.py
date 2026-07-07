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
from .utils import send_resend_email
from django.views.decorators.csrf import csrf_exempt
from .services import create_promote_record
from .services import create_promote_record, update_student_grade
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Member
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Member
from .serializers import MemberSerializer
import random
from django.core.mail import send_mail
from django.shortcuts import redirect
from .services import teacher_email_exists
from .decorators import teacher_login_required
from .services import get_teacher_by_email
from .services import (get_teacher_by_email, get_teacher_grade_assignments, get_student_records)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.shortcuts import render
from .services import get_student_records, get_teacher_grade_assignments, get_attendance_records
from .services import (get_teacher_by_email, get_schedule_class_records, get_student_records)
from .services import (get_teacher_by_email, get_schedule_class_records, get_student_records, get_teacher_students)


@csrf_exempt
def send_grade_mail(request):

    print("REQUEST RECEIVED")

    if request.method != "POST":
        return JsonResponse({"error": "POST only"})
    

    
def view_records(request):
    data = get_zoho_records("school-app", "Student_Report")
    return render(request, 'attendance/list.html', {'students': data})

def home(request):
    from .utils import IntiateOauth
    from .services import get_teacher_records
    return HttpResponse(f"Refresh Token Success. Access Token:  {get_teacher_records()}")

@teacher_login_required
def view_teachers(request):
    teachers = get_teacher_records()
    
    # 1. Fetch the logged-in teacher's profile using their session email
    email = request.session.get("email")
    current_teacher = get_teacher_by_email(email)

    return render(
        request,
        "attendance/list.html",
        {
            "teachers": teachers,
            "teacher": current_teacher  # 2. Add this so list.html can read {{ teacher.Name.first_name }}
        }
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

@teacher_login_required
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

@teacher_login_required
def student_marks_page(request):

    students = get_student_records()

    selected_grade = request.GET.get("grade")
    selected_year = request.GET.get("year")

    if selected_grade:
        students = [
            s for s in students
            if s.get("Class_Grade") == selected_grade
        ]

    if selected_year:
        students = [
            s for s in students
            if s.get("Academic_Year") == selected_year
        ]

    academic_years = []

    for student in get_student_records():
        year = student.get("Academic_Year")
        if year and year not in academic_years:
            academic_years.append(year)

    return render(
        request,
        "attendance/student_marks.html",
        {
            "students": students,
            "academic_years": academic_years,
            "selected_grade": selected_grade,
            "selected_year": selected_year,
        }
    )

@csrf_exempt
def save_marks(request):

    print("Req received")

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

    if request.method != "POST":
        return JsonResponse({"error": "POST only"})

    body = json.loads(request.body)
    print(body)

    grade = body["grade"]
    academic_year = body["academic_year"]

    subject = body["subject"]
    # exam_date = body["exam_date"]
    # exam_time = body["exam_time"]
    message = body["message"]

    final_message = f"""
    Academic Year : {academic_year}

    Grade : {grade}

    {message}
    """

    students = get_student_records()

    send_count = 0

    for student in students:

        if (
            student.get("Class_Grade") == grade
            and
            student.get("Academic_Year") == academic_year
        ):

            email_address = student.get("Student_Email")

            if not email_address:
                continue

            notification_type = body["notification_type"]
            template_name = f"emails/{notification_type}.html"

            html_content = render_to_string(
                template_name,
                {
                    "student_name": student["Student_Name"]["zc_display_value"],
                    "academic_year": academic_year,
                    "grade": grade,
                    "message": message,
                }
            )

            success = send_resend_email(
                subject=subject,
                message=final_message,
                to_emails=[email_address],
                html_content=html_content
            )

            if success:
                print("Mail sent:", email_address)
                send_count += 1
            else:
                print("MAIL ERROR: Resend API failed")

            # send_count += 1

            print(f"Mail sent to: {email_address}")

    print(f"Total mails sent: {send_count}")

    return JsonResponse({
        "count": send_count
    })


@teacher_login_required
def send_mail_page(request):

    selected_grade = request.GET.get("grade")
    selected_year = request.GET.get("year")

    students = get_student_records()

    if selected_grade:
        students = [
            s for s in students
            if s.get("Class_Grade") == selected_grade
        ]

    if selected_year:
        students = [
            s for s in students
            if s.get("Academic_Year") == selected_year
        ]

    academic_years = []

    for student in get_student_records():
        year = student.get("Academic_Year")
        if year and year not in academic_years:
            academic_years.append(year)

    return render(
        request,
        "attendance/send_mail.html",
        {
            "students": students,
            "academic_years": academic_years,
            "selected_grade": selected_grade,
            "selected_year": selected_year,
        }
    )

@teacher_login_required
def promote_students_page(request):

    selected_grade = request.GET.get("grade")
    selected_year = request.GET.get("year")

    students = get_student_records()

    if selected_grade:
        students = [
            s for s in students
            if s.get("Class_Grade") == selected_grade
        ]

    if selected_year:
        students = [
            s for s in students
            if s.get("Academic_Year") == selected_year
        ]

    academic_years = []

    for student in get_student_records():
        year = student.get("Academic_Year")
        if year and year not in academic_years:
            academic_years.append(year)

    return render(
        request,
        "attendance/promote_students.html",
        {
            "students": students,
            "academic_years": academic_years,
            "selected_grade": selected_grade,
            "selected_year": selected_year,
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

from django.http import JsonResponse

def get_students_api(request):
    students = get_student_records()
    return JsonResponse({
        "students": students
    })



@api_view(['GET'])
def member_list_api(request):

    members = Member.objects.all()

    serializer = MemberSerializer(
        members,
        many=True
    )

    return Response(serializer.data)

def teacher_login(request):

    if request.method == "POST":

        email = request.POST.get("email")

        if not teacher_email_exists(email):

            return render(
                request,
                "attendance/login.html",
                {
                    "error": "Email not found"
                }
            )

        otp = str(random.randint(100000, 999999))

        request.session["otp"] = otp
        request.session["email"] = email

        send_resend_email(
            subject="Teacher Login OTP",
            message=f"Your OTP is {otp}",
            to_emails=[email]
        )

        return redirect("verify_otp")

    return render(
        request,
        "attendance/login.html"
    )


def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        if entered_otp == request.session.get("otp"):

            request.session["teacher_logged_in"] = True

            user_agent = request.META.get(
                "HTTP_USER_AGENT",
                ""
            ).lower()

            is_mobile = (
                "android" in user_agent
                or "iphone" in user_agent
                or "mobile" in user_agent
            )

            # MOBILE → Dashboard page
            if is_mobile:
                return redirect("teacher_dashboard")

            # DESKTOP → Teacher Portal cards
            return redirect("teachers")

        return render(
            request,
            "attendance/verify_otp.html",
            {"error": "Invalid OTP"}
        )

    return render(
        request,
        "attendance/verify_otp.html"
    )


def logout_view(request):

    request.session.flush()

    return redirect("login")



@teacher_login_required
def teacher_profile(request):

    email = request.session.get("email")

    teacher = get_teacher_by_email(email)

    return render(
        request,
        "attendance/profile.html",
        {
            "teacher": teacher
        }
    )



@teacher_login_required
def my_classes(request):

    from collections import defaultdict

    email = request.session.get("email")

    teacher = get_teacher_by_email(email)

    if not teacher:
        return render(
            request,
            "attendance/my_classes.html",
            {
                "teacher": None,
                "grades": [],
                "students": [],
                "grouped_students": {}
            }
        )

    teacher_id = str(teacher.get("ID"))
    print("LOGIN TEACHER ID =", teacher_id)

    assignments = get_schedule_class_records()
    for assignment in assignments:
        print("ASSIGNMENT =", assignment)

    students = get_student_records()

    assigned_grades = []
    my_students = []

    for assignment in assignments:

        teacher_lookup = assignment.get(
            "Select_Teacher",
            {}
        )

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

        assigned_grades.append(
            f"{grade_name} ({assignment_year})"
        )

        for student in students:

            student_grade = student.get(
                "Class_Grade"
            )

            student_year = student.get(
                "Academic_Year"
            )

            if (
                student_grade == grade_name
                and
                student_year == assignment_year
            ):
                my_students.append(student)

    grouped_students = defaultdict(list)

    for student in my_students:

        grade = student.get("Class_Grade", "")
        year = student.get("Academic_Year", "")

        # Find matching assignment timing
        start_time = ""
        end_time = ""
        start_date = ""
        end_date = ""

        for assignment in assignments:

            teacher_lookup = assignment.get("Select_Teacher", {})

            if str(teacher_lookup.get("ID", "")) != teacher_id:
                continue

            assignment_year = assignment.get(
                "Select_Academic_Year", {}
            ).get("Academic_Year", "")

            grade_name = assignment.get(
                "Select_Grade", {}
            ).get("Grade_name", "")

            if grade == grade_name and year == assignment_year:
                start_date = assignment.get("Class_Start_Date", "")
                end_date = assignment.get("Class_End_Date", "")

                start_time = assignment.get("Class_Start_Time", "")
                end_time = assignment.get("Class_End_Time", "")
                break

        key = (
            grade,
            year,
            start_date,
            end_date,
            start_time,
            end_time
        )

        grouped_students[key].append(student)

    print("Teacher ID =", teacher_id)
    print("Assigned Grades =", assigned_grades)
    print("Students Found =", len(my_students))

    for key, student_list in grouped_students.items():
        print(
            f"Grade {key[0]} - Year {key[1]} = {len(student_list)} students"
        )
    
    print("Grouped Students:")
    for key, value in grouped_students.items():
        print(key, len(value))

    return render(
        request,
        "attendance/my_classes.html",
        {
            "teacher": teacher,
            "grades": assigned_grades,
            "students": my_students,
            "grouped_students": dict(grouped_students)
        }
    )
    

@teacher_login_required
def send_class_schedule_mail(request):


    if request.method != "POST":
        return redirect("my_classes")

    grade = request.POST.get("grade")
    academic_year = request.POST.get("academic_year")

    # class_date = request.POST.get("class_date")
    # start_time = request.POST.get("start_time")
    # end_time = request.POST.get("end_time")

    subject = request.POST.get("subject")
    message = request.POST.get("message")

    students = get_student_records()

    email_list = []

    for student in students:

        
        student_grade = student.get(
            "Class_Grade"
        )

        student_year = student.get(
            "Academic_Year"
        )

        if (
            student_grade == grade
            and
            student_year == academic_year
        ):

            email = student.get(
                "Student_Email"
            )

            if email:
                email_list.append(email)

    final_message = f"""
Dear Student,

A class has been scheduled.

-----------------------------------
Grade          : {grade}
Academic Year  : {academic_year}


-----------------------------------

Message:

{message}

Regards,
Teacher
"""

    if email_list:

        send_resend_email(
            subject=subject,
            message=final_message,
            to_emails=email_list
        )

        print(
            f"Mail sent to {len(email_list)} students"
        )

    return redirect("my_classes")

def attendance_page(request):

    selected_grade = request.GET.get("grade")
    selected_year = request.GET.get("year")

    students = get_student_records()  # your Zoho/Django student data

    academic_years = [
        "2025-2026",
        "2026-2027",
        "2027-2028"
    ]

    return render(
        request,
        "attendance/student_list.html",
        {
            "students": students,
            "academic_years": academic_years,
            "selected_grade": selected_grade,
            "selected_year": selected_year,
        }
    )


@teacher_login_required
def teacher_dashboard(request):

    teacher_email = request.session.get("email")
    teacher = get_teacher_by_email(teacher_email)
    teacher_students = get_teacher_students(teacher_email)
    teacher_name = ""
    teacher_role = ""
    if teacher:
        teacher_role = teacher.get("Teacher_Role", "")
    if teacher:
        name_obj = teacher.get("Name", {})
        teacher_name = (
            f"{name_obj.get('first_name', '')} "
            f"{name_obj.get('last_name', '')}"
        ).strip()

    teacher_role = teacher.get("Teacher_Role", "")
    teacher_students = get_teacher_students(teacher_email)

    total_students = len(teacher_students)

    allocated_grades = len(
        set(
            student.get("Class_Grade")
            for student in teacher_students
        )
    )

    attendance = get_attendance_records()
    present_count = 0

    absent_count = 0

    attendance = get_attendance_records()
    attendance_map = {}

    for record in attendance:

        student_name = record.get("Student_Name")

        status = record.get("Attendance_Status")

        if student_name not in attendance_map:

            attendance_map[student_name] = {
                "present": 0,
                "absent": 0
            }

        if status == "Present":
            attendance_map[student_name]["present"] += 1
            present_count += 1
        else:
            attendance_map[student_name]["absent"] += 1
            absent_count += 1

    attendance_percentage = 0

    if present_count + absent_count > 0:

        attendance_percentage = round(
            (present_count / (present_count + absent_count)) * 100
        )

    print("Teacher =", teacher)
    print("Teacher Name =", teacher_name)
    print("Total Students =", total_students)

    print("Teacher Students:")
    for student in teacher_students:
        print(
            student["Student_Name"]["zc_display_value"],
            student["Class_Grade"],
            student["Academic_Year"]
        )

    context = {
        "teacher_name": teacher_name,
        "teacher_role": teacher_role,
        "students": teacher_students,
        "total_students": total_students,
        "allocated_grades": allocated_grades,
        "attendance_percentage": attendance_percentage,
    }

    return render(
        request,
        "attendance/dashboard.html",
        context
    )



            