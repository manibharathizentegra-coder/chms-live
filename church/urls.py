# church/urls.py
from django.urls import path
from . import views
from .views import view_teachers
from .views import attendance_page, view_students
from .views import save_attendance
from .views import student_marks_page
from .views import save_marks
from .views import send_grade_mail
from .views import send_mail_page
from .views import promote_students_page
from .views import save_promotion
from django.urls import path
from . import views


urlpatterns = [
    # This means when you visit 'http://127.0.0.1:8000/', you see the teachers list
    path('', views.teacher_login, name='home'),
    path('dashboard/', view_teachers, name='teachers'),
    path('students/', view_students),
    path('save-attendance/', save_attendance),
    path('student-marks/', student_marks_page),
    path('save-marks/', save_marks),
    path('send-mail/', send_mail_page), 
    path("send-grade-mail/",send_grade_mail),
    path("test/", views.send_mail_page, name="send_mail_page"),
    path("promote-students/", promote_students_page),
    path("save-promotion/", save_promotion),
    path("api/students/", views.get_students_api),
    path('api/members/',views.member_list_api,name='member_list_api'),
    path("save-attendance/", save_attendance),
    path("save-marks/", save_marks),
    path("send-grade-mail/", send_grade_mail),
    path("save-promotion/", save_promotion),
    path("login/", views.teacher_login, name="login"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.teacher_profile, name="profile"),
    path("my-classes/", views.my_classes, name="my_classes"),
    path('test', views.home, name='test'),
    path("send-class-schedule-mail/", views.send_class_schedule_mail, name="send_class_schedule_mail"),
    path('student-list/', views.attendance_page, name='student_list'),
    path('student-marks/', views.student_marks_page, name='students_marks_page'),
    path("teacher-dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path(
        "student-marks/",
        views.student_marks_page,
        name="students_marks_page"
    ),

    path(
        "send-mail/",
        views.send_mail_page,
        name="send_mail_page"
    ),

    path(
        "promote-students/",
        views.promote_students_page,
        name="promote_students_page"
    )
]


