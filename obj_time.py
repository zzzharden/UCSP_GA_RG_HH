import copy
import random
import math
import time

from obj_function import obj_func_all, obj_func_all_print, obj_func_detail, obj_func_time
import numpy as np
from data_loader import data,data1,data2
from fig_gtt import plot_schedule
import matplotlib.pyplot as plt

total_weeks = 16
days_per_week = 5
timeslots_per_day = 5
total_timeslots = days_per_week * timeslots_per_day
classrooms = data2(r'C:\Users\zhuzizhuang\Desktop\classrooms.xlsx')
def schedule_courses(courses_task, classes, teachers, schedule_all):
    # 初始化排课表
    schedule = np.full((len(classrooms), total_timeslots), None)
    # 按班级数量降序排序课程
    courses_task = sorted(courses_task, key=lambda x: -len(x['class']))

    while True:
        # 初始化班级和教师的排课时间表
        class_schedule = {i: set() for i in classes}
        teacher_schedule = {i['name']: set() for i in teachers}

        # 初始化可用时间段的字典
        available_timeslots_dict = {}
        for classroom in classrooms:
            classroom_type = classroom['type']
            if classroom_type not in available_timeslots_dict:
                available_timeslots_dict[classroom_type] = []
            for i in range(total_timeslots):
                if schedule_all[classrooms.index(classroom)][i] is None:
                    available_timeslots_dict[classroom_type].append((i, classrooms.index(classroom)))

        success = True
        for course in courses_task:
            remaining_duration = course['duration']
            while remaining_duration > 0:
                dtime = min(remaining_duration, total_weeks)
                allowed_types = course['allowed_classrooms']
                available_timeslots = []
                for classroom_type in allowed_types:
                    if classroom_type in available_timeslots_dict:
                        for timeslot, classroom_index in available_timeslots_dict[classroom_type]:
                            all_classes_available = all(
                                timeslot not in class_schedule[class_id] for class_id in course['class'])
                            if all_classes_available and timeslot not in teacher_schedule[course['teacher']]:
                                available_timeslots.append((timeslot, classroom_index))

                if not available_timeslots:
                    print(f"无法安排课程: {course}")
                    success = False
                    break

                probability = random.random()
                used_classroom_timeslots = [(ts, ci) for ts, ci in available_timeslots if
                                            any(schedule_all[ci])]
                if probability < 0.97 and used_classroom_timeslots:
                    start_timeslot, classroom_index = random.choice(used_classroom_timeslots)
                else:
                    start_timeslot, classroom_index = random.choice(available_timeslots)

                # 更新排课表
                schedule[classroom_index][start_timeslot] = {
                    'id': course['id'], 'course': course['course'], 'class': course['class'],
                    'teacher': course['teacher'], 'duration': course['duration'],
                    'allowed_classrooms': course['allowed_classrooms'],
                    'time': dtime
                }
                schedule_all[classroom_index][start_timeslot] = {
                    'id': course['id'], 'course': course['course'], 'class': course['class'],
                    'teacher': course['teacher'], 'duration': course['duration'],
                    'allowed_classrooms': course['allowed_classrooms'],
                    'time': dtime
                }

                # 更新班级和教师的排课时间表
                for class_id in course['class']:
                    class_schedule[class_id].add(start_timeslot)
                teacher_schedule[course['teacher']].add(start_timeslot)

                # 从可用时间段字典中移除已使用的时间段
                classroom_type = classrooms[classroom_index]['type']
                available_timeslots_dict[classroom_type].remove((start_timeslot, classroom_index))

                remaining_duration -= dtime
            if not success:
                break

        if not success:
            print("排课失败，正在重新排课...")
            # 清空排课表
            for i in range(len(schedule)):
                for j in range(len(schedule[i])):
                    if schedule[i][j]:
                        schedule[i][j] = None
                        schedule_all[i][j] = None
        else:
            return schedule, class_schedule, teacher_schedule

def initialize_population(paths):
    c_sol = []
    schedule_all = np.full((len(classrooms), total_timeslots), None)
    for i, path in enumerate(paths):
        college_name = f'学院{i + 1}'
        courses_task, teachers, classes, _ = data1(path)
        res, cr, tr = schedule_courses(courses_task, classes, teachers,schedule_all)
        c_sol.append([res, cr, tr, path,schedule_all])
    return c_sol


def A_random(res, cr, tr, schedule_all):
    for x in range(1):
        used_classroom_indices = []
        for classroom_index in range(len(res)):
            if any(res[classroom_index]):
                used_classroom_indices.append(classroom_index)

        room=copy.deepcopy(used_classroom_indices)
        time_a=[]
        for i in range(0,24):
           time_a.append(i)

        for j in range(0,1):
            t1=random.choice(time_a)
            for k in range(0,len(used_classroom_indices)):
                r1=random.choice(room)
                if res[r1][t1]:
                    break
                else:
                    room.remove(r1)

            used_classroom_indices1 = []
            for classroom_index in used_classroom_indices:
                if classrooms[classroom_index]['type'] in res[r1][t1]['allowed_classrooms']:
                    used_classroom_indices1.append(classroom_index)
            r2 = random.choice(used_classroom_indices1)

            swap_time=[]
            for t2 in range(0,24):
                if schedule_all[r2][t2] is None or (res[r2][t2]['course'] != res[r1][t1]['course'] and classrooms[t2]['type'] in res[r1][t1][
                'allowed_classrooms']) :
                    if check(r2,t2,r1,t1,res,cr,tr):
                        swap_time.append(t2)
            if len(swap_time)==0:
                time_a.remove(t1)
                continue
            else:
                t2=random.choice(swap_time)
                update(r2, t2, r1, t1, res, cr, tr)
                res[r1][t1], res[r2][t2] = res[r2][t2], res[r1][t1]
                schedule_all[r1][t1], schedule_all[t1][t1] = schedule_all[r2][t2], schedule_all[r1][t1]
                break

    return [res, cr, tr]


def update(r1, p1, r2, p2, res, cr, tr):
    if p2 in tr[res[r2][p2]['teacher']]:
        tr[res[r2][p2]['teacher']].remove(p2)
        tr[res[r2][p2]['teacher']].add(p1)

    if res[r1][p1]:
        if p1 in tr[res[r1][p1]['teacher']]:
            tr[res[r1][p1]['teacher']].remove(p1)
            tr[res[r1][p1]['teacher']].add(p2)

    for class_id in res[r2][p2]['class']:
        if p2 in cr[class_id]:
            cr[class_id].remove(p2)
            cr[class_id].add(p1)
    if res[r1][p1]:
        for class_id in res[r1][p1]['class']:
            if p1 in cr[class_id]:
                cr[class_id].remove(p1)
                cr[class_id].add(p2)
    return cr, tr


def check(r1, p1, r2, p2, res, cr, tr):
    if p1 in tr[res[r2][p2]['teacher']]:
        # print("教师时间冲突2")
        return False
    elif res[r1][p1] and p2 in tr[res[r1][p1]['teacher']]:
        # print("教师时间冲突1")
        return False

    if res[r1][p1]:
        for class_id in res[r1][p1]['class']:
            if p2 in cr[class_id]:
                # print("班级时间冲突1")
                return False

    for class_id in res[r2][p2]['class']:
        if p1 in cr[class_id]:
            # print("班级时间冲突2")
            return False
    return True

def A_random_old(res, cr, tr,schedule_all):
    for x in range(1):
        used_classroom_indices = []
        for classroom_index in range(len(res)):
            if any(res[classroom_index]):
                used_classroom_indices.append(classroom_index)

        while True:
            p1 = random.randint(0, 24)
            M = random.choice(used_classroom_indices)
            if res[M][p1]:
                break

        used_classroom_indices1 = []
        for classroom_index in used_classroom_indices:
            if classrooms[classroom_index]['type'] in res[M][p1]['allowed_classrooms']:
                used_classroom_indices1.append(classroom_index)

        time_a=[]
        for i in range(0,24):
           time_a.append(i)

        n = 0
        while n < 24: #检查的最大次数
            n = n + 1
            # 从列表中随机选择一个整数
            p = random.choice(time_a)
            r = random.choice(used_classroom_indices1)
            if (res[r][p] and (res[r][p]['course'] != res[M][p1]['course'] and classrooms[M]['type'] in res[r][p][
                'allowed_classrooms'])) or schedule_all[r][p] is None:
                if check(r, p, M, p1, res, cr, tr):
                    update(r, p, M, p1, res, cr, tr)
                    res[r][p], res[M][p1] = res[M][p1], res[r][p]
                    schedule_all[r][p], schedule_all[M][p1] = schedule_all[M][p1], schedule_all[r][p]
                    break
            else:
                time_a.remove(p)

    return [res, cr, tr]

paths = [
    r'large\data1_4.xlsx',
    # r'large\data2.xlsx',
    # r'large\data3.xlsx',
    # r'large\data4.xlsx',
    # r'large\data5.xlsx',
    # r'large\data6.xlsx',
    # r'large\data7.xlsx',
    # r'large\data8.xlsx',
    # r'large\data9.xlsx',
    # r'large\data10.xlsx',
]
start=time.time()
res=initialize_population(paths)
end=time.time()

print("生成时间:",end-start)

obj_value = obj_func_detail(res[0][0],paths[0],classrooms,res[0][2])

print(obj_value)
# time1=0
# time2=0
#
# for i in range(0,10000):
#     start=time.time()
#     A_random(res[0][0],res[0][1],res[0][2],res[0][4])
#     end=time.time()
#     time1=end-start+time1
#
#     start=time.time()
#     A_random_old(res[0][0],res[0][1],res[0][2],res[0][4])
#     end=time.time()
#
#     time2= end - start + time2
#
# print("改变时间:",time1,time2)


# start=time.time()
# obj_value = 0
# res_t=[0,0,0,0,0,0]
# for i, path in enumerate(paths):
#     obj_value = obj_func_time(res[0][0],paths[0],classrooms,res[0][2]) + obj_value
#
# end=time.time()
#
# print("计算时间:",end-start)
