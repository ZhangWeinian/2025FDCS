"""
URL configuration for FDCS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve

from FDCSM.view import account, myAdmin, myProfessor, myStudent

urlpatterns = [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
        name="media",
    ),
    # 管理员
    path("admin_info/", myAdmin.admin_info),
    path("admin_info/add/", myAdmin.admin_add),
    path("admin_info/delete/", myAdmin.admin_delete),
    path("admin_info/detail/", myAdmin.admin_detail),
    path("admin_info/edit/", myAdmin.admin_edit),
    path("admin_info/status/", myAdmin.status),
    path("admin_info/status_s/", myAdmin.status_s),
    path("admin_info/select/", myAdmin.selectEnd),
    path("admin_info/deleteAdmin/", myAdmin.deleteAdmin),
    path("admin_info/outExcel/", myAdmin.export_excel),
    # 导师
    path("professor_info/", myProfessor.professor_info),
    path("professor_info/add/", myProfessor.professor_add),
    path("professor_info/excel_add/", myProfessor.professor_excel_add),
    path("professor_info/delete/", myProfessor.professor_delete),
    path("professor_info/detail/", myProfessor.professor_detail),
    path("professor_info/edit/", myProfessor.professor_edit),
    path("professor_info/excel_temp/", myProfessor.professor_excel_temp),
    path("professor_info/professor_chose/", myProfessor.professor_chose),
    path("professor_info/professor_select/", myProfessor.professor_select),
    path(
        "professor_info/professor_select_delect/", myProfessor.professor_select_delect
    ),
    # 学生
    path("student_info/", myStudent.student_info),
    path("student_info/add/", myStudent.student_add),
    path("student_info/delete/", myStudent.student_delete),
    path("student_info/detail/", myStudent.student_detail),
    path("student_info/edit/", myStudent.student_edit),
    path("student_info/excel_add/", myStudent.student_excel_add),
    path("student_info/excel_temp/", myStudent.student_excel_temp),
    path("student_info/student_chose/", myStudent.student_chose),
    path("student_info/student_select/", myStudent.student_select),
    path("student_info/delete_sel/", myStudent.student_delete_sel),
    path("student_info/upload/", myStudent.student_upload),
    path("login/", account.login),
    path("logout/", account.logout),
    path("stu_login/", account.stu_login),
    path("stu_logout/", account.stu_logout),
    path("pfs_login/", account.pfs_login),
    path("pfs_logout/", account.pfs_logout),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
