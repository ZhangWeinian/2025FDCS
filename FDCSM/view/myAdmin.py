from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from import_export.formats import base_formats

from FDCSM import models
from FDCSM.utils.pagination import Pagination
from FDCSM.view.myModelForm import AdminModelForm, OutExcel


def admin_info(request):
    # 管理员信息
    form = AdminModelForm()
    querySet = models.FDC_ADM_INFO.objects.all()
    page_object = Pagination(request, querySet)
    context = {
        "form": form,
        "queryset": page_object.page_queryset,
        "page_string": page_object.html(),
    }
    return render(request, "admin_info.html", context)


#


@csrf_exempt
def admin_add(request):
    form = AdminModelForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def admin_delete(request):
    uid = request.GET.get("uid")
    models.FDC_ADM_INFO.objects.filter(ADM_NBR=uid).delete()
    return JsonResponse({"status": True})


def admin_detail(request):
    uid = request.GET.get("uid")
    row_dict = (
        models.FDC_ADM_INFO.objects.filter(ADM_NBR=uid)
        .values("ADM_NBR", "ADM_NAM", "ADM_PWD")
        .first()
    )
    if not row_dict:
        return JsonResponse({"status": False, "error": "数据不存在。"})
    return JsonResponse({"status": True, "data": row_dict})


def admin_edit(request):
    uid = request.GET.get("uid")
    row_obj = models.FDC_ADM_INFO.objects.filter(ADM_NBR=uid).first()
    if not row_obj:
        return JsonResponse({"status": False, "tips": "数据不存在！"})
    form = AdminModelForm(data=request.POST, instance=row_obj)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False, "error": form.errors})


def status(request):
    import django.utils.timezone as timezone

    status = {
        0: "开启学生选择志愿",
        1: "开启导师第一志愿",
        2: "开启导师第二志愿",
        3: "开启导师第三志愿",
    }
    start_obj = models.FDC_STAT_INFO.objects.all()
    if start_obj.first() is None:
        models.FDC_STAT_INFO.objects.create(STAT_ID=0, CHG_TIM=timezone.now)
        return JsonResponse({"status": True, "alert": "开启学生选择志愿"})
    status_now = (start_obj[0].STAT_ID + 1) % 4
    start_obj.update(STAT_ID=status_now, CHG_TIM=timezone.now())
    return JsonResponse({"status": True, "alert": status[status_now]})


def status_s(request):
    import django.utils.timezone as timezone

    status_choise = {
        0: "开启学生选择志愿",
        1: "开启导师第一志愿",
        2: "开启导师第二志愿",
        3: "开启导师第三志愿",
    }
    status = request.GET.get("status")
    start_obj = models.FDC_STAT_INFO.objects.all()
    if start_obj.first() is None:
        models.FDC_STAT_INFO.objects.create(STAT_ID=int(status), CHG_TIM=timezone.now)
        return JsonResponse({"status": True, "alert": "开启学生选择志愿"})
    # status_now = (start_obj[0].STAT_ID + 1) % 4
    start_obj.update(STAT_ID=int(status), CHG_TIM=timezone.now())
    return JsonResponse({"status": True, "alert": status_choise[int(status)]})


def selectEnd(request):
    querySet = models.FDC_PFS_SEL.objects.all()
    page_object = Pagination(request, querySet)
    context = {"queryset": page_object.page_queryset, "page_string": page_object.html()}
    return render(request, "select.html", context)


def deleteAdmin(request):
    stu_id = request.GET.get("stu_id")
    pfs_id = request.GET.get("pfs_id")
    obj = models.FDC_PFS_SEL.objects.filter(PFS_NBR=pfs_id, PFS_STU_NBR=stu_id).first()
    if obj:
        obj.delete()
    models.FDC_STU_INFO.objects.filter(STU_NBR=stu_id).update(STU_TYP=0)
    return redirect("/admin_info/select/")


def export_excel(request):
    queryset = models.FDC_PFS_SEL.objects.all()
    dataset = OutExcel().export(queryset)
    excel_format = base_formats.XLSX()
    response = HttpResponse(
        excel_format.export_data(dataset),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="selection_results.xlsx"'
    return response
