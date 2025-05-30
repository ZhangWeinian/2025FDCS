import json

from django.conf import settings
from django.shortcuts import HttpResponse, redirect
from django.utils.deprecation import MiddlewareMixin

from FDCSM import models


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ignore_list = ["/login/", "/stu_login/", "/pfs_login/"]
        if request.path_info in ignore_list:
            return
        info_dict = request.session.get("info")
        status = models.FDC_STAT_INFO.objects.all().first()
        if status is None:
            return False
        # 管理员访问页面
        admin_views = ["/admin_info/", "/professor_info/", "/student_info/"]
        if request.path_info in admin_views:
            admin_object = models.FDC_ADM_INFO.objects.filter(
                ADM_NBR=info_dict["id"]
            ).first()
            if admin_object:
                return
            return redirect("/login/")
        # 导师访问页面
        pfs_views = ["/professor_info/professor_chose/"]
        if request.path_info in pfs_views:
            # if status.STAT_ID not in [0, 1, 2, 3]:
            if status.STAT_ID not in [1, 2, 3]:
                return redirect("/pfs_login/")
            pfs_object = models.FDC_PFS_INFO.objects.filter(
                PFS_NBR=info_dict["id"]
            ).first()
            if pfs_object:
                return
            return redirect("/pfs_login/")
        # 学生访问页面
        stu_views = ["/student_info/student_chose/", "/student_info/upload/"]
        if request.path_info in stu_views:
            if status.STAT_ID not in [0]:
                return redirect("/stu_login/")
            stu_object = models.FDC_STU_INFO.objects.filter(
                STU_NBR=info_dict["id"]
            ).first()
            if stu_object:
                return
            return redirect("/stu_login/")
