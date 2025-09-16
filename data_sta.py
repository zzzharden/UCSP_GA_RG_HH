import pandas as pd
from openpyxl.workbook import Workbook


def load_courses(file_path,sheet):
    """
    读取课程数据文件，返回课程任务列表。
    """
    df = pd.read_excel(file_path,sheet_name=sheet)
    return df.shape[0]

def load_teachers(file_path,sheet):
    """
    读取教师数据文件，返回教师列表。
    """
    df = pd.read_excel(file_path,sheet_name=sheet)

    return df.shape[0]

def load_classes(file_path,sheet):
    """
    读取班级数据文件，返回班级列表。
    """
    df = pd.read_excel(file_path,sheet_name=sheet)


    return df.shape[0]



def data(path):
    courses_task = load_courses(path, "CT_test")
    # classrooms = load_classrooms(path, "CR")
    teachers = load_teachers(path, "M_T")
    classes = load_classes(path, "CL")
    return classes,courses_task,teachers


data(r'data/large_new\data1_4.xlsx')
paths = [
    r'large_new\data1_4.xlsx',
    r'large_new\data2.xlsx',
    r'large_new\data3.xlsx',
    r'large_new\data4.xlsx',
    r'large_new\data5.xlsx',
    r'large_new\data6.xlsx',
    r'large_new\data7.xlsx',
    r'large_new\data8.xlsx',
    r'large_new\data9.xlsx',
    r'large_new\data10.xlsx',
]

wb = Workbook()
ws = wb.active
ws.title = 'e'

# 写入表头
ws.append(['Instance','College', 'Class', 'Course_task', 'Teacher', 'Classroom'])

num=[]
for index,path in enumerate(paths):
    s=data(path)
    print('学院',index+1,",",data(path))
    num.append(s)

res=[0,0,0]
row_data=[]
ord=0
for index,n in enumerate(num):
    res[0] = res[0] + num[index][0]
    res[1] = res[1] + num[index][1]
    res[2] = res[2] + num[index][2]

    ord=ord+1
    ws.append([f'Instance{ord}',index+1,res[0],res[1],res[2],(index+1)*20])
    print(index+1,"个学院：",res)

name='instance.xlsx'
wb.save(name)


