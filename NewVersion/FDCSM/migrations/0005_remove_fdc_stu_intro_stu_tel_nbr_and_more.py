# Generated by Django 5.0.4 on 2024-04-27 06:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("FDCSM", "0004_alter_fdc_stu_intro_stu_tel_nbr"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="fdc_stu_intro",
            name="STU_TEL_NBR",
        ),
        migrations.AddField(
            model_name="fdc_stu_info",
            name="STU_TEL_NBR",
            field=models.CharField(
                default=18223161844, max_length=20, verbose_name="电话号码"
            ),
            preserve_default=False,
        ),
    ]
