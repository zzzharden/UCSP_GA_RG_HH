import pandas as pd


def load_courses(file_path,sheet):
    """
    读取课程数据文件，返回课程任务列表。
    """
    df = pd.read_excel(file_path,sheet_name=sheet)
    courses_task = []
    for index, row in df.iterrows():
        # 将 class 和 cr_type 列的逗号分隔字符串转换为列表
        class_list = [x.strip() for x in str(row['class']).split(',')] if pd.notna(row['class']) else []
        cr_type_list = [x.strip() for x in str(row['cr_type']).split(',')] if pd.notna(row['cr_type']) else []

        course = {
            'id': row['id'],
            'class': class_list,
            'course': row['course'],
            'teacher': row['teacher'],
            'duration': int(row['time']),
            'type': row['type'],
            'allowed_classrooms': cr_type_list,
            'start_week': row['start_week']
        }
        courses_task.append(course)

    return courses_task


def load_classrooms(file_path,sheet):
    """
    读取教室数据文件，返回教室列表。
    """
    df = pd.read_excel(file_path,sheet_name=sheet)
    classrooms = []
    for index, row in df.iterrows():
        cr = {
            'order':row['id'],
            'id': row['name'],
            'type': row['type']
        }
        classrooms.append(cr)

    return classrooms


def load_teachers(file_path,sheet):
    """
    读取教师数据文件，返回教师列表。
    """
    df = pd.read_excel(file_path,sheet_name=sheet)
    teachers = []
    for index, row in df.iterrows():
        like_list1 = [int(x.strip()) for x in str(row['like1']).split(',')] if pd.notna(row['like1']) else []
        # like_list2 = [int(x.strip()) for x in str(row['like2']).split(',')] if pd.notna(row['like2']) else []
        t = {
            'name': row['name'],
            'like1': like_list1,
            # 'like2': like_list2,
            'like3':row['like3']

        }
        teachers.append(t)

    return teachers


def load_classes(file_path,sheet):
    """
    读取班级数据文件，返回班级列表。
    """
    df = pd.read_excel(file_path,sheet_name=sheet)
    classes = []
    for index, row in df.iterrows():
        classes.append(str(row['name']))

    return classes

def load_c(file_path,sheet):
    """
    读取课程数据文件，返回班级列表。
    """
    df = pd.read_excel(file_path,sheet_name=sheet)
    courses = []
    for index, row in df.iterrows():
        like_list = [int(x.strip()) for x in str(row['like']).split(',')] if pd.notna(row['like']) else []
        c = {
            'name': row['name'],
            'like': like_list
        }
        courses.append(c)

    return courses

def data(path):
    courses_task = load_courses(path, "CT_test")
    classrooms = load_classrooms(path, "CR")
    teachers = load_teachers(path, "M_T")
    classes = load_classes(path, "CL")
    courses = load_c(path, "M_C")
    return courses_task, classrooms, teachers, classes, courses

def data1(path):
    courses_task = load_courses(path, "CT_test")
    teachers = load_teachers(path, "M_T")
    classes = load_classes(path, "CL")
    courses = load_c(path, "M_C")
    return courses_task, teachers, classes, courses

def data2(path):
    classrooms = load_classrooms(path,"CR")
    return classrooms

