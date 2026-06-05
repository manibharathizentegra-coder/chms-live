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

urlpatterns = [
    # This means when you visit 'http://127.0.0.1:8000/', you see the teachers list
    path('', view_teachers, name='teachers'),
    path('students/', view_students),
    path('save-attendance/', save_attendance),
    path('student-marks/', student_marks_page),
    path('save-marks/', save_marks),
    path('send-mail/', send_mail_page), 
    path("send-grade-mail/",send_grade_mail),
    path("test/", views.send_mail_page, name="send_mail_page"),
    path("promote-students/", promote_students_page),
    path("save-promotion/", save_promotion),
]


