from django import forms
from django.shortcuts import redirect, render

from FDCSM import models


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=True,
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=True,
    )


def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})
    form = LoginForm(request.POST)
    if form.is_valid():
        admin_object = models.FDC_ADM_INFO.objects.filter(
            ADM_NBR=form.cleaned_data["username"], ADM_PWD=form.cleaned_data["password"]
        ).first()
        if not admin_object:
            form.add_error("password", "用户名或密码错误")
            return render(request, "login.html", {"form": form})

        request.session["info"] = {
            "id": admin_object.ADM_NBR,
            "name": admin_object.ADM_NAM,
        }
        return redirect("/admin_info/")

    return render(request, "login.html", {"form": form})


def logout(request):
    request.session.clear()
    return redirect("/login/")


def stu_login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "stu_login.html", {"form": form})
    form = LoginForm(request.POST)
    if form.is_valid():
        stu_object = models.FDC_STU_INFO.objects.filter(
            STU_NBR=form.cleaned_data["username"], STU_PWD=form.cleaned_data["password"]
        ).first()
        if not stu_object:
            form.add_error("password", "用户名或密码错误")
            return render(request, "stu_login.html", {"form": form})

        request.session["info"] = {"id": stu_object.STU_NBR, "name": stu_object.STU_NAM}
        return redirect("/student_info/student_chose/")
    return render(request, "stu_login.html", {"form": form})


def stu_logout(request):
    request.session.clear()
    return redirect("/stu_login/")


def pfs_login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "pfs_login.html", {"form": form})
    form = LoginForm(request.POST)
    if form.is_valid():
        pfs_object = models.FDC_PFS_INFO.objects.filter(
            PFS_NBR=form.cleaned_data["username"], PFS_PWD=form.cleaned_data["password"]
        ).first()
        if not pfs_object:
            form.add_error("password", "用户名或密码错误")
            return render(request, "stu_login.html", {"form": form})

        request.session["info"] = {"id": pfs_object.PFS_NBR, "name": pfs_object.PFS_NAM}
        return redirect("/professor_info/professor_chose/")
    return render(request, "pfs_login.html", {"form": form})


def pfs_logout(request):
    request.session.clear()
    return redirect("/pfs_login/")
