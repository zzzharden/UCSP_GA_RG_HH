import copy
import random
import time
from collections import defaultdict

import numpy as np
from fig_gtt import plot_schedule, plot_teacher_schedule, plot_class_schedule, plot_class_heatmap, plot_schedule1
import random
from data_loader import data,data1,data2
from obj_function import obj_func_all, obj_func_all_print, obj_func_detail
import matplotlib.pyplot as plt

total_weeks = 16
days_per_week = 5
timeslots_per_day = 5
total_timeslots = days_per_week * timeslots_per_day
classrooms = data2(r'classrooms.xlsx')

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
                    'classroom': classrooms[classroom_index]['id'],'allowed_classrooms':course['allowed_classrooms'],
                    'time': dtime
                }
                schedule_all[classroom_index][start_timeslot] = {
                    'id': course['id'], 'course': course['course'], 'class': course['class'],
                    'teacher': course['teacher'], 'duration': course['duration'],
                    'classroom': classrooms[classroom_index]['id'],'allowed_classrooms':course['allowed_classrooms'],
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


# 生成初始解的函数，具体实现需根据问题定义
def initialize_population(paths):
    c_sol = []
    schedule_all = np.full((len(classrooms), total_timeslots), None)
    for i, path in enumerate(paths):
        college_name = f'学院{i + 1}'
        courses_task, teachers, classes, courses = data1(path)
        res, cr, tr = schedule_courses(courses_task, classes, teachers,schedule_all)
        c_sol.append([res, cr, tr, teachers, courses, schedule_all])
    return c_sol


# 根据低层次启发式向量LVa更新服务组合向量SVa，具体实现需根据问题定义
def update_sva(v,i):

    s = [v[0], v[1], v[2]]
    if i == 0:
        s = A_swap_random_timeslots(v[0], v[1], v[2],v[5])
    elif i == 1:
        s = A_reverse_consecutive_timeslots(v[0], v[1], v[2],v[5])
    elif i == 2:
        s = A_swap_classroom_type_timeslots(v[0], v[1], v[2],v[5])
    elif i == 3:
        s = A_random(v[0], v[1], v[2],v[5])
    elif i == 4:
        s = B_night(v[0], v[1], v[2],v[5])
    elif i == 5:
        s = B_course(v[0], v[1], v[2],v[5])
    elif i == 6:
        s = B_c_course(v[0], v[1], v[2],v[4],v[5])
    elif i==7:
        s = B_c_teacher(v[0], v[1], v[2],v[3],v[5])
    elif i==8:
        s = B_method(v[0], v[1], v[2],v[3],v[5])

    s.append(v[3])
    s.append(v[4])
    s.append(v[5])
    v = s

    return v

def A_swap_random_timeslots(schedule, class_schedule, teacher_schedule,schedule_all):

    # 找出使用过的教室的索引
    used_classroom_indices = []
    for classroom_index in range(len(schedule_all)):
        if any(schedule_all[classroom_index]):
            used_classroom_indices.append(classroom_index)

    """
    随机交换排课表中的两列元素（两个时间段），并同步更新班级和教师的时间表

    参数:
    schedule (list): 排课表，二维数组，格式为 [教室][时间段]
    class_schedule (dict): 班级时间表，{班级ID: 已排课的时间段集合}
    teacher_schedule (dict): 教师时间表，{教师姓名: 已排课的时间段集合}

    返回:
    tuple: (交换后的排课表, 班级时间表, 教师时间表, 被交换的两个时间段索引)
    """


    # 随机选择两个不同的时间段
    timeslot1, timeslot2 = random.sample(range(total_timeslots), 2)

    # 1. 更新班级和教师时间表
    # 收集所有课程涉及的班级和教师
    classes_involved = set()
    teachers_involved = set()

    # 遍历所有教室的这两个时间段
    for classroom_idx in range(len(schedule)):
        # 处理时间段1的课程
        course1 = schedule[classroom_idx][timeslot1]
        if course1:
            classes_involved.update(course1['class'])
            teachers_involved.add(course1['teacher'])

        # 处理时间段2的课程
        course2 = schedule[classroom_idx][timeslot2]
        if course2:
            classes_involved.update(course2['class'])
            teachers_involved.add(course2['teacher'])

    # 更新班级时间表：交换两个时间段的记录
    for class_id in classes_involved:
        slots = class_schedule[class_id]
        has_slot1 = timeslot1 in slots
        has_slot2 = timeslot2 in slots

        if has_slot1 and not has_slot2:
            slots.remove(timeslot1)
            slots.add(timeslot2)
        elif has_slot2 and not has_slot1:
            slots.remove(timeslot2)
            slots.add(timeslot1)
        elif has_slot1 and has_slot2:
            pass  # 两个时间段都有课，无需修改
        else:
            pass  # 两个时间段都没课，无需修改

    # 更新教师时间表：交换两个时间段的记录
    for teacher_id in teachers_involved:
        slots = teacher_schedule[teacher_id]
        has_slot1 = timeslot1 in slots
        has_slot2 = timeslot2 in slots

        if has_slot1 and not has_slot2:
            slots.remove(timeslot1)
            slots.add(timeslot2)
        elif has_slot2 and not has_slot1:
            slots.remove(timeslot2)
            slots.add(timeslot1)
        elif has_slot1 and has_slot2:
            pass  # 两个时间段都有课，无需修改
        else:
            pass  # 两个时间段都没课，无需修改

    # 2. 交换排课表中的两个时间段
    for classroom in schedule:
        classroom[timeslot1], classroom[timeslot2] = classroom[timeslot2], classroom[timeslot1]
        for i in used_classroom_indices:
            if classroom[timeslot1] and classrooms[i]['id']==classroom[timeslot1]['classroom']:
                schedule_all[i][timeslot1],schedule_all[i][timeslot2]=schedule_all[i][timeslot2],schedule_all[i][timeslot1]
            elif classroom[timeslot2] and classrooms[i]['id']==classroom[timeslot2]['classroom']:
                schedule_all[i][timeslot1],schedule_all[i][timeslot2]=schedule_all[i][timeslot2],schedule_all[i][timeslot1]

    return [schedule, class_schedule, teacher_schedule]

def A_reverse_consecutive_timeslots(schedule, class_schedule, teacher_schedule, schedule_all):
    """
    随机选择2到4个连续的时间段并将它们倒序排列，同时更新班级、教师和全局的时间表

    参数:
    schedule (list): 排课表，二维数组，格式为 [教室][时间段]
    class_schedule (dict): 班级时间表，{班级ID: 已排课的时间段集合}
    teacher_schedule (dict): 教师时间表，{教师姓名: 已排课的时间段集合}
    schedule_all (list): 全局排课表，二维数组，格式为 [教室索引][时间段]
    classrooms (list): 教室信息列表，包含教室ID等信息

    返回:
    tuple: (交换后的排课表, 班级时间表, 教师时间表, 全局排课表, 被倒序的时间段范围)
    """

    # 随机确定连续时间段的长度（2-4）
    block_size = min(random.randint(2, 4), total_timeslots)

    # 随机选择起始位置
    start_idx = random.randint(0, total_timeslots - block_size)
    end_idx = start_idx + block_size - 1

    # 创建时间段的倒序列表
    reversed_indices = list(range(start_idx, end_idx + 1))[::-1]

    # 1. 更新班级和教师时间表
    # 收集所有课程涉及的班级和教师
    classes_involved = set()
    teachers_involved = set()

    # 遍历所有教室的这个时间段块
    for classroom_idx in range(len(schedule)):
        for original_idx in range(start_idx, end_idx + 1):
            course = schedule[classroom_idx][original_idx]
            if course:
                classes_involved.update(course['class'])
                teachers_involved.add(course['teacher'])

    # 创建新旧时间段的映射
    time_mapping = {original: new_idx for original, new_idx in
                    zip(range(start_idx, end_idx + 1), reversed_indices)}

    # 更新班级时间表
    for class_id in classes_involved:
        slots = class_schedule[class_id]
        # 找出在倒序块中的时间段
        slots_in_block = [slot for slot in slots if start_idx <= slot <= end_idx]

        # 移除这些时间段
        for slot in slots_in_block:
            slots.remove(slot)

        # 添加倒序后的时间段
        for slot in slots_in_block:
            slots.add(time_mapping[slot])

    # 更新教师时间表
    for teacher_id in teachers_involved:
        slots = teacher_schedule[teacher_id]
        # 找出在倒序块中的时间段
        slots_in_block = [slot for slot in slots if start_idx <= slot <= end_idx]

        # 移除这些时间段
        for slot in slots_in_block:
            slots.remove(slot)

        # 添加倒序后的时间段
        for slot in slots_in_block:
            slots.add(time_mapping[slot])

    # 2. 倒序排课表中的时间段块
    for classroom_idx in range(len(schedule)):
        # 提取需要倒序的时间段
        block = [schedule[classroom_idx][i] for i in range(start_idx, end_idx + 1)]
        # 倒序后放回原位置
        for i, course in zip(range(start_idx, end_idx + 1), reversed(block)):
            schedule[classroom_idx][i] = course

    # 3. 更新schedule_all中的对应记录
    # 建立教室ID到schedule_all索引的映射
    classroom_id_to_index = {classroom['id']: idx for idx, classroom in enumerate(classrooms)}

    # 对每个教室处理倒序块
    for classroom in schedule:
        # 遍历倒序块中的每个时间段
        for original_idx, new_idx in zip(range(start_idx, end_idx + 1), reversed_indices):
            course = classroom[original_idx]
            if course:
                # 找到该课程对应的教室在schedule_all中的索引
                classroom_id = course.get('classroom')
                if classroom_id and classroom_id in classroom_id_to_index:
                    schedule_all_idx = classroom_id_to_index[classroom_id]
                    # 更新schedule_all中对应位置
                    schedule_all[schedule_all_idx][original_idx] = course.copy()
                    # 更新课程中的时间信息
                    schedule_all[schedule_all_idx][original_idx]['time'] = new_idx - start_idx + 1

    return [schedule, class_schedule, teacher_schedule]

def A_swap_classroom_type_timeslots(schedule, class_schedule, teacher_schedule, schedule_all):
    """
    随机交换两个时间段中某一类教室的所有元素，同时更新班级、教师和全局的时间表

    参数:
    schedule (list): 排课表，二维数组，格式为 [教室][时间段]
    class_schedule (dict): 班级时间表，{班级ID: 已排课的时间段集合}
    teacher_schedule (dict): 教师时间表，{教师姓名: 已排课的时间段集合}
    schedule_all (list): 全局排课表，二维数组，格式为 [教室索引][时间段]
    classrooms (list): 教室信息列表，包含教室ID和类型等信息

    返回:
    tuple: (交换后的排课表, 班级时间表, 教师时间表, 全局排课表, 被交换的时间段索引, 教室类型)
    """
    # 获取所有教室类型
    classroom_types = list({classroom['type'] for classroom in classrooms})

    # 确保有可用的教室类型
    if not classroom_types:
        print("警告: 没有找到可用的教室类型")
        return schedule, class_schedule, teacher_schedule, schedule_all, (None, None), None

    # 随机选择一种教室类型
    selected_type = random.choice(classroom_types)

    # 获取该类型教室在schedule中的索引
    type_indices = [i for i, classroom in enumerate(classrooms) if classroom['type'] == selected_type]

    # 确保该类型有教室
    if not type_indices:
        print(f"警告: 教室类型 {selected_type} 没有对应的教室")
        return schedule, class_schedule, teacher_schedule, schedule_all, (None, None), None

    # 随机选择两个不同的时间段
    timeslot1, timeslot2 = random.sample(range(total_timeslots), 2)

    # 1. 更新班级和教师时间表
    # 收集所有课程涉及的班级和教师
    classes_involved = set()
    teachers_involved = set()

    # 遍历该类型的所有教室
    for classroom_idx in type_indices:
        # 处理时间段1的课程
        course1 = schedule[classroom_idx][timeslot1]
        if course1:
            classes_involved.update(course1['class'])
            teachers_involved.add(course1['teacher'])

        # 处理时间段2的课程
        course2 = schedule[classroom_idx][timeslot2]
        if course2:
            classes_involved.update(course2['class'])
            teachers_involved.add(course2['teacher'])

    # 更新班级时间表：交换两个时间段的记录
    for class_id in classes_involved:
        slots = class_schedule[class_id]
        has_slot1 = timeslot1 in slots
        has_slot2 = timeslot2 in slots

        if has_slot1 and not has_slot2:
            slots.remove(timeslot1)
            slots.add(timeslot2)
        elif has_slot2 and not has_slot1:
            slots.remove(timeslot2)
            slots.add(timeslot1)
        elif has_slot1 and has_slot2:
            pass  # 两个时间段都有课，无需修改
        else:
            pass  # 两个时间段都没课，无需修改

    # 更新教师时间表：交换两个时间段的记录
    for teacher_id in teachers_involved:
        slots = teacher_schedule[teacher_id]
        has_slot1 = timeslot1 in slots
        has_slot2 = timeslot2 in slots

        if has_slot1 and not has_slot2:
            slots.remove(timeslot1)
            slots.add(timeslot2)
        elif has_slot2 and not has_slot1:
            slots.remove(timeslot2)
            slots.add(timeslot1)
        elif has_slot1 and has_slot2:
            pass  # 两个时间段都有课，无需修改
        else:
            pass  # 两个时间段都没课，无需修改

    # 2. 交换排课表中该类型教室的两个时间段
    for classroom_idx in type_indices:
        schedule[classroom_idx][timeslot1], schedule[classroom_idx][timeslot2] = \
            schedule[classroom_idx][timeslot2], schedule[classroom_idx][timeslot1]

    # 3. 更新schedule_all中的对应记录
    # 建立教室ID到schedule_all索引的映射
    classroom_id_to_index = {classroom['id']: idx for idx, classroom in enumerate(classrooms)}

    # 对该类型的每个教室处理交换
    for classroom_idx in type_indices:
        classroom_id = classrooms[classroom_idx]['id']
        if classroom_id in classroom_id_to_index:
            schedule_all_idx = classroom_id_to_index[classroom_id]
            # 交换schedule_all中的对应时间段
            schedule_all[schedule_all_idx][timeslot1], schedule_all[schedule_all_idx][timeslot2] = \
                schedule_all[schedule_all_idx][timeslot2], schedule_all[schedule_all_idx][timeslot1]

    return [schedule, class_schedule, teacher_schedule]

def A_random(res, cr, tr,schedule_all):
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
        n = 0
        while n < 100: #检查的最大次数
            n = n + 1
            # 从列表中随机选择一个整数
            p = random.randint(0, 24)
            r = random.choice(used_classroom_indices1)
            if (res[r][p] and (res[r][p]['course'] != res[M][p1]['course'] and classrooms[M]['type'] in res[r][p][
                'allowed_classrooms'])) or schedule_all[r][p] is None:
                if check(r, p, M, p1, res, cr, tr):
                    res[r][p], res[M][p1] = res[M][p1], res[r][p]
                    schedule_all[r][p], schedule_all[M][p1] = schedule_all[M][p1], schedule_all[r][p]
                    break
    return [res, cr, tr]


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


def B_night(res, cr, tr,schedule_all):
    for x in range(5):
        p1 = random.choice([4, 9, 14, 19, 24])
        M = 0
        V = 0
        for i in range(len(classrooms)):
            if res[i][p1] is not None and res[i][p1]['time'] * len(res[i][p1]['class']) > V:
                M = i
                V = res[i][p1]['time'] * len(res[i][p1]['class'])
        if res[M][p1] is None:
            continue

        nums = [i for i in range(25) if i not in [4, 9, 14, 19, 24]]
        used_classroom_indices = []
        for classroom_index in range(len(res)):
            if any(res[classroom_index]) and classrooms[classroom_index]['type'] in res[M][p1]['allowed_classrooms']:
                used_classroom_indices.append(classroom_index)
        sign = True
        n = 0
        while sign and n < 100:
            n = n + 1
            # 从列表中随机选择一个整数
            p = random.choice(nums)
            r = random.choice(used_classroom_indices)

            if (res[r][p] and res[r][p]['time'] * len(res[r][p]['class']) < V) or schedule_all[r][p] is None:
                if check(r, p, M, p1, res, cr, tr):
                    res[r][p], res[M][p1] = res[M][p1], res[r][p]
                    schedule_all[r][p], schedule_all[M][p1] = schedule_all[M][p1], schedule_all[r][p]
                    break
    return [res, cr, tr]


def B_course(res, cr, tr,schedule_all):
    for x in range(2):
        class_course_days = defaultdict(lambda: defaultdict(set))
        re_list = []
        for ord, classroom in enumerate(res):
            for timeslot, course_info in enumerate(classroom):
                if course_info:
                    day = timeslot // timeslots_per_day
                    sign = 0
                    for class_id in course_info['class']:
                        for c in class_course_days[class_id][day]:
                            if course_info['course'] == c[0]:
                                sign = 1
                                re_list.append([ord, timeslot])
                        if sign == 0:
                            class_course_days[class_id][day].add((course_info['course'], course_info['time']))
        if len(re_list)==0:
            return [res,cr,tr]

        first = random.choice(re_list)
        M, p1 = first[0], first[1]
        used_classroom_indices = []
        for classroom_index in range(len(res)):
            if any(res[classroom_index]) and classrooms[classroom_index]['type'] in res[M][p1]['allowed_classrooms']:
                used_classroom_indices.append(classroom_index)
        n = 0
        while n < 100:
            n = n + 1
            # 从列表中随机选择一个整数
            p = random.randint(0, 24)
            r = random.choice(used_classroom_indices)
            if (res[r][p] and (res[r][p]['course'] != res[M][p1]['course'] and classrooms[M]['type'] in res[r][p][
                'allowed_classrooms'])) or schedule_all[r][p] is None:
                if check(r, p, M, p1, res, cr, tr):
                    res[r][p], res[M][p1] = res[M][p1], res[r][p]
                    schedule_all[r][p], schedule_all[M][p1] = schedule_all[M][p1], schedule_all[r][p]
                    break
    return [res, cr, tr]


def B_c_course(res, cr, tr,courses,schedule_all):

    for x in range(10):
        while True:
            used_classroom_indices=[]
            used_indices=[]
            for i in range(len(res)):
                for j in range(0,25):
                    if res[i][j]:
                        used_indices.append([i,j])
                        used_classroom_indices.append(i)

            u = random.choice(used_indices)
            M,p1=u[0],u[1]
            used_classroom_indices1 = []
            for classroom_index in used_classroom_indices:
                if classrooms[classroom_index]['type'] in res[M][p1]['allowed_classrooms']:
                    used_classroom_indices1.append(classroom_index)

            like_time = []
            for course in courses:
                if res[M][p1]['course'] == course['name']:
                    if course['like'][p1 % 5] == -1:
                        for index, c in enumerate(course['like']):
                            if c == 1 or c == 0:
                                like_time.append(index)
                    elif course['like'][p1 % 5] == 0:
                        for index, c in enumerate(course['like']):
                            if c == 1:
                                like_time.append(index)
                    break
            if len(like_time) > 0:
                break

        nums = [i for i in range(25) if i % 5 in like_time]

        n = 0
        while n < 100:
            n = n + 1
            # 从列表中随机选择一个整数
            p = random.choice(nums)
            r = random.choice(used_classroom_indices1)
            if (res[r][p] and (res[r][p]['course'] != res[M][p1]['course'] and classrooms[M]['type'] in res[r][p][
                'allowed_classrooms'])) or schedule_all[r][p] is None:
                if check(r, p, M, p1, res, cr, tr):
                    res[r][p], res[M][p1] = res[M][p1], res[r][p]
                    schedule_all[r][p], schedule_all[M][p1] = schedule_all[M][p1], schedule_all[r][p]
                    break
    return [res, cr, tr]



def B_c_teacher(res, cr, tr,teachers,schedule_all):
    for x in range(10):
        while True:
            used_classroom_indices=[]
            used_indices=[]
            for i in range(len(res)):
                for j in range(0,25):
                    if res[i][j]:
                        used_indices.append([i,j])
                        used_classroom_indices.append(i)

            u = random.choice(used_indices)
            M,p1=u[0],u[1]
            used_classroom_indices1 = []
            for classroom_index in used_classroom_indices:
                if classrooms[classroom_index]['type'] in res[M][p1]['allowed_classrooms']:
                    used_classroom_indices1.append(classroom_index)

            like_time = []
            for teacher in teachers:
                if res[M][p1]['teacher'] == teacher['name']:
                    if teacher['like1'][p1 // 5] == -1:
                        for index1, t1 in enumerate(teacher['like1']):
                            if t1 >= 0:
                                like_time.append(index1)

                    elif teacher['like1'][p1 // 5] == 0:
                        for index1, t1 in enumerate(teacher['like1']):
                            if t1  >= 1:
                                like_time.append(index1)

                    break
            if len(like_time) > 0:
                break

        nums = [i for i in range(25) if i // 5 in like_time]
        n = 0
        while n < 100:
            n = n + 1
            # 从列表中随机选择一个整数
            p = random.choice(nums)
            r = random.choice(used_classroom_indices1)
            if res[r][p] and (res[r][p]['course'] != res[M][p1]['course'] and classrooms[M]['type'] in res[r][p][
                'allowed_classrooms']) :
                if check(r, p, M, p1, res, cr, tr):
                    res[r][p], res[M][p1] = res[M][p1], res[r][p]
                    schedule_all[r][p], schedule_all[M][p1] = schedule_all[M][p1], schedule_all[r][p]
                    break
    return [res, cr, tr]


def B_method(res, cr, tr,teachers,schedule_all):
    used_classroom_indices = []
    pairs = [(0, 1), (2, 3), (5, 6), (7, 8), (10, 11), (12, 13), (15, 16), (17, 18), (20, 21), (22, 23)]
    for classroom_index in range(len(res)):
        if any(res[classroom_index]):
            used_classroom_indices.append(classroom_index)
    # print("cr:",used_classroom_indices)
    for x in range(2):
        while True:
            M = random.choice(used_classroom_indices)
            used_classroom_time_indices = []
            for i in range(25):
                if res[M][i]:
                    used_classroom_time_indices.append(i)
            if used_classroom_time_indices is None:
                print(classrooms['id'][M])
                plot_schedule(res,classrooms)
                break

            p1 = random.choice(used_classroom_time_indices)
            tt = res[M][p1]['teacher']

            like_time = []
            no = []
            swap_list = []
            for teacher in teachers:
                if res[M][p1]['teacher'] == teacher['name']:

                    if teacher['like3'] == 1:
                        for pair in pairs:
                            # 检查集合中是否同时包含括号内的两个数字
                            if pair[0] in tr[teacher['name']] and pair[1] not in tr[teacher['name']]:
                                if res[M][pair[1]]:
                                    like_time.append(pair[1])
                            elif pair[0] not in tr[teacher['name']] and pair[1] in tr[teacher['name']]:
                                if res[M][pair[0]]:
                                    like_time.append(pair[0])
                            elif pair[0]  in tr[teacher['name']] and pair[1] in tr[teacher['name']]:
                                no.append(pair[0])
                                no.append(pair[1])
                        break

            if len(like_time) > 0:
                break

        sign = True
        while len(like_time) > 0 and sign:

            p = random.choice(like_time)
            for pair in pairs:
                if pair[0] == p:
                    no.append(pair[1])
                elif pair[1] == p:
                    no.append(pair[0])

            for t in tr[teacher['name']]:
                if t not in no:
                    swap_list.append(t)
            like_time.remove(p)

            while len(swap_list) > 0:
                p1 = random.choice(swap_list)
                swap_list.remove(p1)

                for classroom_index in used_classroom_indices:
                    if res[classroom_index][p1] and res[classroom_index][p1]['teacher'] == tt:
                        M = classroom_index
                        break
                if res[M][p1] is None:
                    break
                used_classroom_indices1 = []
                for classroom_index in used_classroom_indices:
                    if classrooms[classroom_index]['type'] in res[M][p1]['allowed_classrooms']:
                        used_classroom_indices1.append(classroom_index)

                # 从列表中随机选择一个整数
                r = random.choice(used_classroom_indices1)
                if res[r][p] and check(r, p, M, p1, res, cr, tr):
                    res[r][p], res[M][p1] = res[M][p1], res[r][p]
                    schedule_all[r][p], schedule_all[M][p1] = schedule_all[M][p1], schedule_all[r][p]
                    sign = False
                    break

    return [res, cr, tr]


if __name__ == "__main__":
    paths = [
        r'large_new\data1_4.xlsx',
        # r'large_new\data2.xlsx',
    ]
    # paths = [
    #     r'small_new\l_data01.xlsx',
    # ]


    initial_solution = initialize_population(paths)
    time_records = []  # 存储 (序号, 执行时间) 元组

    # 生成0-8的有序列表
    nums = list(range(9))
    # 随机打乱顺序
    random.shuffle(nums)

    for idx in nums:
        start = time.time()
        update_sva(initial_solution[0], idx)
        end = time.time()
        # 记录序号（从1开始）和执行时间
        time_records.append((idx + 1, end - start))

    # 按执行时间升序排序（根据时间值排序，保留序号）
    sorted_records = sorted(time_records, key=lambda x: x[1])

    # 输出排序结果（带序号）
    print("排序结果（序号-原始顺序，时间-秒）:")
    for rank, (original_idx, time) in enumerate(sorted_records, 1):
        print(f"第{rank}名: 原始序号{original_idx}, 时间{time:.4f}秒")



