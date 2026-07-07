from django.shortcuts import redirect

def teacher_login_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.session.get("teacher_logged_in"):
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return wrapper