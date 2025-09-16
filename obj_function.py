import time
from collections import defaultdict

from data_loader import data,data1
import numpy as np



total_weeks = 16
days_per_week = 5
timeslots_per_day = 5
weight=[2,2,1,1,1,2,1]


def calculate_night_course(schedule):
    p1 = 0
    # 预计算所有晚上课程的索引位置（每天最后一个时间段）
    night_slots = {n * timeslots_per_day - 1 for n in range(1, (len(schedule[0]) // timeslots_per_day) + 1)}

    # 展开为两层循环优化版
    for classroom in schedule:  # 直接遍历元素而非索引
        for j, course in enumerate(classroom):
            if course and j in night_slots:
                p1 += course['time'] * len(course['class'])
    return p1

# 通用的分布计算函数
def preprocess_distributions(schedule, classes):
    # 创建班级ID到数组索引的映射
    class_id_to_idx = {c: i for i, c in enumerate(classes)}
    num_classes = len(classes)

    # 使用三维数组存储分布数据 [class_idx, week, day]
    class_distribution = np.zeros((num_classes, total_weeks, days_per_week), dtype=np.int16)

    # 预先计算时间槽到天数的映射
    timeslot_to_day = np.arange(days_per_week * timeslots_per_day) // timeslots_per_day

    class_hours=0
    for classroom_idx, classroom_schedule in enumerate(schedule):
        for timeslot, course_info in enumerate(classroom_schedule):
            if course_info:
                class_hours=class_hours+course_info['time']
                day_idx = timeslot_to_day[timeslot]
                time_weeks = min(course_info['time'], total_weeks)  # 限制最大周数

                # 批量更新所有相关周
                weeks = np.arange(time_weeks)
                for class_id in course_info['class']:
                    class_idx = class_id_to_idx[class_id]
                    class_distribution[class_idx, weeks, day_idx] += 1

    return class_distribution,class_hours


def evaluate_class_distribution(class_distribution):
    # 直接使用预处理好的数据进行计算
    weekly_std = np.std(class_distribution, axis=2)  # 按周和班级计算每日标准差
    mean_std = np.mean(weekly_std, axis=1)  # 每个班级的周平均标准差
    return np.mean(mean_std)  # 全局平均值


def teacher_continuity(teachers,tr):
    p3=0
    num=0
    pairs = [(0, 1), (2, 3), (5, 6), (7, 8), (10, 11), (12, 13), (15, 16), (17, 18), (20, 21), (22, 23)]
    # like=[]
    # no=[]
    for t in tr:
        #s=[]
        for pair in pairs:
            # 检查集合中是否同时包含括号内的两个数字
            if pair[0] in tr[t] and pair[1] in tr[t]:
                #s.append(pair)
                num += 1
        num1=(len(tr[t])-num*2)//2
        for teacher in teachers:
            if teacher['name']==t:
                if(teacher['like3']==1):
                    #like.append(s)
                    p3=p3+num
                elif(teacher['like3']==-1):
                    #no.append(s)
                    p3=p3+num1
                break
        num=0
    # print(like)
    # print(no)
    return p3*10



# 教师偏好时间
def teacher_like(schedule, teachers):
    p4 = 0
    # 预处理：构建老师到课程时间和时长的映射
    teacher_courses = {}
    for i in range(len(schedule)):
        for j in range(len(schedule[0])):
            course = schedule[i][j]
            if course:
                teacher_name = course['teacher']
                if teacher_name not in teacher_courses:
                    teacher_courses[teacher_name] = []
                teacher_courses[teacher_name].append((j, course['time']))

    # 计算每个老师的满意度
    for t in teachers:
        teacher_name = t['name']
        if teacher_name not in teacher_courses:
            continue
        like1 = t['like1']  # 减少字典访问
        for j, time in teacher_courses[teacher_name]:
            day_index = j // timeslots_per_day
            p4 += like1[day_index] * time
    return p4

# 课程偏好时间
def course_like(schedule, courses):
    p5 = 0
    # 预处理：构建课程到课程时间和时长的映射
    course_slots = {}
    for i in range(len(schedule)):
        for j in range(len(schedule[0])):
            if schedule[i][j]:
                course_name = schedule[i][j]['course']
                time_slot = j % timeslots_per_day  # 提前计算时间槽索引
                if course_name not in course_slots:
                    course_slots[course_name] = []
                course_slots[course_name].append((time_slot, schedule[i][j]['time']))

    # 计算每个课程的满意度
    for c in courses:
        course_name = c['name']
        if course_name not in course_slots:
            continue
        like = c['like']  # 减少字典访问
        for time_slot, time in course_slots[course_name]:
            p5 += like[time_slot] * time
    return p5


def course_perday(schedule):
    p6 = 0
    num=0
    # 按班级统计每日课程
    class_course_days = defaultdict(lambda: defaultdict(set))
    for classroom in schedule:
        for timeslot, course_info in enumerate(classroom):
            if course_info:
                day = timeslot // timeslots_per_day
                sign = 0
                for class_id in course_info['class']:
                    for x in class_course_days[class_id][day]:
                        if course_info['course'] == x[0]:
                            sign = 1
                            p6 = p6 + min(course_info['time'], x[1])
                            num=num+1
                    if sign == 0:
                        # 将列表转换为元组
                        class_course_days[class_id][day].add((course_info['course'], course_info['time']))
    return p6,num

def cr_num(schedule):
    p7=0
    for index in range(0,len(schedule)):
        if any(schedule[index]):
            p7=p7+1
    return p7

def normalize_value(value, min_val, max_val):
    """归一化函数，将值映射到[0,1]区间"""
    if max_val == min_val:
        return 0.5  # 防止除零错误
    return (value - min_val) / (max_val - min_val)

def obj_func_all(schedule, path, tr, classroom_num,c_num):
    courses_task, teachers, classes, courses = data1(path)
    p1 = calculate_night_course(schedule)
    class_distribution, class_hours = preprocess_distributions(schedule, classes)
    p2 = evaluate_class_distribution(class_distribution)
    p3 = teacher_continuity(teachers, tr)
    p4 = teacher_like(schedule, teachers)
    p5 = course_like(schedule, courses)
    p6, num = course_perday(schedule)
    p7= classroom_num * total_weeks*days_per_week*timeslots_per_day
    p22 = p2 * class_hours

    classroom_obj = len(courses_task) * 2 * total_weeks

    # 归一化处理
    # p1范围: [0, classroom_obj//timeslots_per_day]
    p1_norm = normalize_value(p1, 0, 2*classroom_obj // timeslots_per_day)

    # p2范围: [0, class_hours]
    p22_norm = normalize_value(p22, 0, class_hours)

    # p3范围: [-len(teachers)*10, len(teachers)*10]
    p3_min = -len(teachers) * 10
    p3_max = len(teachers) * 10
    p3_norm = normalize_value(p3, p3_min, p3_max)

    # p4范围: [-classroom_obj, classroom_obj]
    p4_norm = normalize_value(p4, -classroom_obj, classroom_obj)

    # p5范围: [-classroom_obj, classroom_obj]
    p5_norm = normalize_value(p5, -classroom_obj, classroom_obj)

    # p6范围: [0, classroom_obj//2]
    p6_norm = normalize_value(p6, 0, len(courses_task)//2*total_weeks)

    # p7范围: [classroom_obj//2, classroom_obj*2]
    p7_norm = normalize_value(p7, classroom_obj // 2, classroom_obj * 2)/c_num

    # 计算归一化后的目标函数值
    value = (weight[0] * p1_norm +
             weight[1] * p22_norm -
             weight[2] * p3_norm -
             weight[3] * p4_norm -
             weight[4] * p5_norm +
             weight[5] * p6_norm +
             weight[6] * p7_norm)

    return round(value, 4)


def obj_func_detail(schedule,path,classroom_num,tr,c_num):
    courses_task, teachers, classes, courses = data1(path)
    p1 = calculate_night_course(schedule)  # 软约束1：晚上应少分配课程任务
    class_distribution,class_hours = preprocess_distributions(schedule,classes)
    p2 = evaluate_class_distribution(class_distribution)  # 软约束2：班级在一周中要上的课程分布要均匀
    p3 = teacher_continuity(teachers,tr)  # 软约束3：老师尽量分配其喜欢的教学方式
    p4 = teacher_like(schedule,teachers)  # 软约束4：教师教学尽量安排在其偏好时间
    p5 = course_like(schedule,courses)  # 软约束5：课程尽量安排在其合适时间
    p6,num = course_perday(schedule)   #软约束6：相同课程一天不能安排超过一个时间段
    p7= classroom_num * total_weeks*days_per_week*timeslots_per_day
    p22=p2*class_hours

    classroom_obj=len(courses_task)*2*total_weeks

    # 归一化处理
    # p1范围: [0, classroom_obj//timeslots_per_day]
    p1_norm = normalize_value(p1, 0, 2*classroom_obj // timeslots_per_day)

    # p2范围: [0, class_hours]
    p22_norm = normalize_value(p22, 0, class_hours)

    # p3范围: [-len(teachers)*10, len(teachers)*10]
    p3_min = -len(teachers) * 10
    p3_max = len(teachers) * 10
    p3_norm = normalize_value(p3, p3_min, p3_max)

    # p4范围: [-classroom_obj, classroom_obj]
    p4_norm = normalize_value(p4, -classroom_obj, classroom_obj)

    # p5范围: [-classroom_obj, classroom_obj]
    p5_norm = normalize_value(p5, -classroom_obj, classroom_obj)

    # p6范围: [0, classroom_obj//2]
    p6_norm = normalize_value(p6, 0, len(courses_task)//2*total_weeks)

    # p7范围: [classroom_obj//2, classroom_obj*2]
    p7_norm = normalize_value(p7, classroom_obj // 2, classroom_obj * 2)/c_num

    nor=[round(p1_norm, 4),round(p22_norm, 4),round(p3_norm,4),round(p4_norm,4),round(p5_norm,4),round(p6_norm,4),round(p7_norm,4)]
    ori=[p1,round(p22, 2),p3,p4,p5,p6,p7]

    return [nor,ori]

def obj_func_all_print(schedule,path,classroom_num,tr,c_num):
    courses_task, teachers, classes, courses = data1(path)
    p1 = calculate_night_course(schedule)  # 软约束1：晚上应少分配课程任务
    class_distribution,class_hours = preprocess_distributions(schedule,classes)
    p2 = evaluate_class_distribution(class_distribution)  # 软约束2：班级在一周中要上的课程分布要均匀
    p3 = teacher_continuity(teachers,tr)  # 软约束3：老师尽量分配其喜欢的教学方式
    p4 = teacher_like(schedule,teachers)  # 软约束4：教师教学尽量安排在其偏好时间
    p5 = course_like(schedule,courses)  # 软约束5：课程尽量安排在其合适时间
    p6,num = course_perday(schedule)   #软约束6：相同课程一天不能安排超过一个时间段
    p7= classroom_num * total_weeks*days_per_week*timeslots_per_day
    p22=p2*class_hours

    classroom_obj=len(courses_task)*2*total_weeks

    # 归一化处理
    # p1范围: [0, classroom_obj//timeslots_per_day]
    p1_norm = normalize_value(p1, 0, 2*classroom_obj // timeslots_per_day)

    # p2范围: [0, class_hours]
    p22_norm = normalize_value(p22, 0, class_hours)

    # p3范围: [-len(teachers)*10, len(teachers)*10]
    p3_min = -len(teachers) * 10
    p3_max = len(teachers) * 10
    p3_norm = normalize_value(p3, p3_min, p3_max)

    # p4范围: [-classroom_obj, classroom_obj]
    p4_norm = normalize_value(p4, -classroom_obj, classroom_obj)

    # p5范围: [-classroom_obj, classroom_obj]
    p5_norm = normalize_value(p5, -classroom_obj, classroom_obj)

    # p6范围: [0, classroom_obj//2]
    p6_norm = normalize_value(p6, 0, len(courses_task)//2*total_weeks)

    # p7范围: [classroom_obj//2, classroom_obj*2]
    p7_norm = normalize_value(p7, classroom_obj // 2, classroom_obj * 2)/c_num


    # 计算归一化后的目标函数值
    value = (weight[0] * p1_norm +
             weight[1] * p22_norm -
             weight[2] * p3_norm -
             weight[3] * p4_norm -
             weight[4] * p5_norm +
             weight[5] * p6_norm +
             weight[6] * p7_norm)

    value = round(value, 4)

    print("夜晚安排总课时数:", p1_norm,",",p1)
    print(f"所有班级的课程分布均匀性:{p22_norm}, p2={p2:.4f}")
    print("符合老师教学习惯（离散/连续）净总课时数(符合数量-不符合数量):",p3_norm, ",",p3)
    print('符合教师时间偏好净总课时数(符合数量-不符合数量):',p4_norm,",", p4)
    print('符合课程适合时间净总课时数(符合数量-不符合数量):',p5_norm,",", p5)
    print("班级每天过度安排某门课的总课时数： ",p6_norm,",num:",num,",",p6)
    print("该学院使用教室数量：",cr_num(schedule),",","总：",classroom_num,",",p7_norm)
    print('p1 + p22 - p3 - p4 - p5 + p6:', value)
    return value

def obj_func_time(schedule,path,tr):
    courses_task, teachers, classes, courses = data1(path)
    res_time=[]

    start=time.time()
    p1 = calculate_night_course(schedule)  # 软约束1：晚上应少分配课程任务
    end=time.time()
    res_time.append(end-start)

    start = time.time()
    class_distribution = preprocess_distributions(schedule,classes)
    p2 = evaluate_class_distribution(class_distribution)  # 软约束2：班级在一周中要上的课程分布要均匀
    end=time.time()
    res_time.append(end-start)

    start = time.time()
    p3 = teacher_continuity(teachers,tr)  # 软约束3：老师尽量分配其喜欢的教学方式
    end=time.time()
    res_time.append(end-start)

    start = time.time()
    p4 = teacher_like(schedule,teachers)  # 软约束4：教师教学尽量安排在其偏好时间
    end = time.time()
    res_time.append(end - start)

    start = time.time()
    p5 = course_like(schedule,courses)  # 软约束5：课程尽量安排在其合适时间
    end = time.time()
    res_time.append(end - start)

    start = time.time()
    p6,num = course_perday(schedule)   #软约束6：相同课程一天不能安排超过一个时间段
    end = time.time()
    res_time.append(end - start)

    # start = time.time()
    # p7= cr_num(schedule)   #软约束6：相同课程一天不能安排超过一个时间段
    # end = time.time()
    # res_time.append(end - start)

    print(res_time)
    return res_time


