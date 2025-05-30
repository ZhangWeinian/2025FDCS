import django.utils.timezone as timezone
from django.db import models


# Create your models here.
class FDC_STU_INFO(models.Model):
    STU_NBR = models.CharField(verbose_name="登录账号", max_length=20, primary_key=True)
    STU_PWD = models.CharField(verbose_name="登录密码", max_length=20)
    STU_NAM = models.CharField(verbose_name="姓名", max_length=20)
    STU_TEL_NBR = models.CharField(
        verbose_name="电话号码", max_length=20, blank=True, null=True
    )
    stu_pro_choices = (
        (0, "物理专业"),
        (1, "数学专业"),
        (2, "系统科学专业"),
        (3, "应用统计专业"),  # 新增应用统计专业
        (4, "纳米科学与工程专业"),  # 新增纳米科学与工程专业
    )
    STU_PRO = models.IntegerField(verbose_name="专业", choices=stu_pro_choices)
    stu_typ_choices = ((0, "未被导师录取"), (1, "已被导师录取"))
    STU_TYP = models.IntegerField(
        verbose_name="状态", default=0, choices=stu_typ_choices
    )
    CAT_TIM = models.DateTimeField(verbose_name="用户创建时间", default=timezone.now)
    CHG_TIM = models.DateTimeField(verbose_name="用户更新时间", auto_now=True)

    class Meta:
        db_table = "FDC_STU_INFO"
        verbose_name = "学生基本信息表"


class FDC_STU_INTRO(models.Model):
    STU_NBR = models.OneToOneField(
        FDC_STU_INFO, on_delete=models.CASCADE, primary_key=True
    )
    STU_ONE_SEL = models.ForeignKey(
        to="FDC_PFS_INFO",
        to_field="PFS_NBR",
        on_delete=models.SET_NULL,
        null=True,
        related_name="STU_ONE_SEL",
    )
    STU_TOW_SEL = models.ForeignKey(
        to="FDC_PFS_INFO",
        to_field="PFS_NBR",
        on_delete=models.SET_NULL,
        null=True,
        related_name="STU_TOW_SEL",
    )
    STU_THR_SEL = models.ForeignKey(
        to="FDC_PFS_INFO",
        to_field="PFS_NBR",
        on_delete=models.SET_NULL,
        null=True,
        related_name="STU_THR_SEL",
    )
    STU_GRADE = models.FileField(
        verbose_name="成绩", max_length=100, upload_to="grade/", null=True, blank=True
    )
    STU_VIT = models.FileField(
        verbose_name="简历", max_length=100, upload_to="intro/", null=True, blank=True
    )
    CAT_TIM = models.DateTimeField(verbose_name="用户创建时间", default=timezone.now)
    CHG_TIM = models.DateTimeField(verbose_name="用户更新时间", auto_now=True)

    class Meta:
        db_table = "FDC_STU_INTRO"
        verbose_name = "学生成绩、简历和志愿选择"


class FDC_PFS_INFO(models.Model):
    PFS_NBR = models.CharField(verbose_name="登录号码", max_length=20, primary_key=True)
    PFS_PWD = models.CharField(verbose_name="登录密码", max_length=20)
    PFS_NAM = models.CharField(verbose_name="姓名", max_length=20)
    PFS_TEL_NBR = models.CharField(
        verbose_name="电话号码", max_length=20, blank=True, null=True
    )
    PFS_INTRO = models.TextField(verbose_name="简介", max_length=400, blank=True)
    PFS_NUM_MATH = models.IntegerField(verbose_name="数学专业可选人数", default=0)
    PFS_NUM_PSC = models.IntegerField(verbose_name="物理专业可选人数", default=0)
    PFS_NUM_SCI = models.IntegerField(verbose_name="系统科学专业可选人数", default=0)
    PFS_NUM_AST = models.IntegerField(
        verbose_name="应用统计专业可选人数", default=0
    )  # 新增应用统计专业
    PFS_NUM_NANO = models.IntegerField(
        verbose_name="纳米科学与工程专业可选人数", default=0
    )  # 新增纳米科学与工程专业
    CAT_TIM = models.DateTimeField(verbose_name="用户创建时间", default=timezone.now)
    CHG_TIM = models.DateTimeField(verbose_name="用户更新时间", auto_now=True)

    class Meta:
        db_table = "FDC_PFS_INFO"
        verbose_name = "导师基本信息表"


class FDC_PFS_SEL(models.Model):
    SELECT_ID = models.AutoField(primary_key=True)
    PFS_NBR = models.ForeignKey(
        to="FDC_PFS_INFO", to_field="PFS_NBR", on_delete=models.CASCADE
    )
    PFS_STU_NBR = models.ForeignKey(
        to="FDC_STU_INFO",
        to_field="STU_NBR",
        on_delete=models.SET_NULL,
        null=True,
        related_name="PFS_STU_NBR",
    )
    stu_pro_choices = (
        (0, "物理专业"),
        (1, "数学专业"),
        (2, "系统科学专业"),
        (3, "应用统计专业"),  # 新增应用统计专业
        (4, "纳米科学与工程专业"),  # 新增纳米科学与工程专业
    )
    STU_PRO = models.IntegerField(verbose_name="学生专业", choices=stu_pro_choices)
    PFS_STATE = models.IntegerField(verbose_name="当前状态", default=0)
    CAT_TIM = models.DateTimeField(verbose_name="用户创建时间", auto_now_add=True)
    CHG_TIM = models.DateTimeField(verbose_name="用户更新时间", auto_now=True)

    def get_STU_PRO_display(self):
        return dict(self.stu_pro_choices).get(self.STU_PRO, "未知")

    class Meta:
        db_table = "FDC_PFS_SEL"
        verbose_name = "导师选择结果表"


class FDC_ADM_INFO(models.Model):
    ADM_NBR = models.CharField(verbose_name="登录账号", max_length=20, primary_key=True)
    ADM_NAM = models.CharField(verbose_name="姓名", max_length=20)
    ADM_PWD = models.CharField(verbose_name="登录密码", max_length=20)
    CAT_TIM = models.DateTimeField(verbose_name="用户创建时间", default=timezone.now)
    CHG_TIM = models.DateTimeField(verbose_name="用户更新时间", auto_now=True)

    class Meta:
        db_table = "FDC_ADM_INFO"
        verbose_name = "管理员基本信息表"


class FDC_STAT_INFO(models.Model):
    stat_id_choises = (
        (0, "学生选择状态"),
        (1, "导师选择第一志愿"),
        (2, "导师选择第二志愿"),
        (3, "导师选择第三志愿"),
    )
    STAT_ID = models.IntegerField(
        verbose_name="当前状态", primary_key=True, choices=stat_id_choises
    )
    CAT_TIM = models.DateTimeField(verbose_name="用户创建时间", default=timezone.now)
    CHG_TIM = models.DateTimeField(verbose_name="用户更新时间", auto_now=True)

    class Meta:
        db_table = "FDC_STAT_INFO"
        verbose_name = "状态信息表"


# 日志
# from django.db.models.signals import post_save, post_delete, pre_save
# from django.dispatch import receiver
# class FDC_STU_INFO_LOG(models.Model):
#     message = models.CharField(max_length=255)
#     timestamp = models.DateTimeField(auto_now_add=True)


# 信号处理函数
# @receiver(post_save, sender=FDC_STU_INFO)
# def log_save(sender, **kwargs):
#     instance = kwargs['instance']
#     if hasattr(instance, '_state') and hasattr(instance._state, 'db'):
#         update_fields = getattr(instance._state, 'db')._update_fields
#         print(f"Updated fields: {update_fields}")
# @receiver(post_delete, sender=FDC_STU_INFO)
# def log_delete(sender, **kwargs):
#     message = f"{sender.__class__.__name__} {kwargs['instance'].pk} was deleted"
#     ChangeLog.objects.create(message=message)
