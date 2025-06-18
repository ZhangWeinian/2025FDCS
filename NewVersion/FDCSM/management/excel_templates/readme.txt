运行命令:
准备好你的 Excel 文件 ( initial_admins.xlsx, initial_professors.xlsx, initial_students.xlsx)，然后从项目根目录运行：
python manage.py import_initial_users --professor_file path/to/initial_professors.xlsx --student_file path/to/initial_students.xlsx
或者，如果你在命令中硬编码了文件路径，则直接运行
python manage.py import_initial_users