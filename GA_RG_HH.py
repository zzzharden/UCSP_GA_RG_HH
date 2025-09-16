import copy
import time
from collections import defaultdict
from fig_gtt import *
import random
from data_loader import data, data1, data2
from obj_function import obj_func_all, obj_func_all_print, obj_func_detail
import matplotlib.pyplot as plt

total_weeks = 16
days_per_week = 5
timeslots_per_day = 5
total_timeslots = days_per_week * timeslots_per_day
classrooms = data2(r'classrooms.xlsx')

def schedule_courses(courses_task, classes, teachers, schedule_all, col="1"):
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
                if probability < 0.98 and used_classroom_timeslots:
                    start_timeslot, classroom_index = random.choice(used_classroom_timeslots)
                else:
                    start_timeslot, classroom_index = random.choice(available_timeslots)

                # 更新排课表
                schedule[classroom_index][start_timeslot] = {
                    'id': course['id'], 'course': course['course'], 'class': course['class'],
                    'teacher': course['teacher'], 'duration': course['duration'],
                    'classroom': classrooms[classroom_index]['id'], 'allowed_classrooms': course['allowed_classrooms'],
                    'time': dtime
                }
                schedule_all[classroom_index][start_timeslot] = {
                    'id': col + '-' + str(course['id']), 'course': course['course'], 'class': course['class'],
                    'teacher': course['teacher'], 'duration': course['duration'],
                    'classroom': classrooms[classroom_index]['id'], 'allowed_classrooms': course['allowed_classrooms'],
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
            return schedule, class_schedule, teacher_schedule # 返回更新后的教室列表

# 生成初始解的函数
def generate_initial_solution(paths):
    # 这里只是示例，需要根据实际问题调整
    pop = []
    pop.append([random.randint(0, 9) for _ in range(10)])
    schedule_all = np.full((len(classrooms), total_timeslots), None)
    for i, path in enumerate(paths):
        college_name = f'学院{i + 1}'
        courses_task, teachers, classes, courses = data1(path)
        res, cr, tr = schedule_courses(courses_task, classes, teachers, schedule_all, str(i + 1))
        pop.append([res, cr, tr, teachers, courses, schedule_all])
    return pop


# 锦标赛选择
def selection(population, fitness, tournament_size=5):
    """
    锦标赛选择函数，适应度值越小被选中的概率越高
    :param population: 种群，一个包含多个个体的列表
    :param fitness: 每个个体对应的适应度值列表
    :param tournament_size: 锦标赛规模，默认为5
    :return: 选中的两个个体
    """
    selected_individuals = []
    for _ in range(2):  # 选择两个个体
        # 随机选择 tournament_size 个个体的索引
        tournament_indices = random.sample(range(len(population)), tournament_size)
        # 获取这些个体的适应度值
        tournament_fitness = [fitness[i] for i in tournament_indices]
        # 找到适应度值最小的个体的索引（因为适应度越小越好）
        min_fitness_index = tournament_indices[tournament_fitness.index(min(tournament_fitness))]
        # 添加到选中列表
        selected_individuals.append(copy.deepcopy(population[min_fitness_index]))
    return selected_individuals[0], selected_individuals[1]


# 两点交叉策略
def two_point_crossover(parent1, parent2):
    """
    两点交叉策略函数
    :param parent1: 父代个体1
    :param parent2: 父代个体2
    :return: 生成的子代个体
    """
    # 确保染色体长度至少为2，以便进行两点交叉
    if len(parent1) < 2 or len(parent2) < 2:
        raise ValueError("染色体长度必须至少为2才能进行两点交叉")

    # 随机选择两个不同的交叉点
    point1, point2 = sorted(random.sample(range(1, len(parent1)), 2))

    # 生成子代个体，两点之间的部分来自parent2，其余部分来自parent1
    child = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
    return child


# 单点变异策略函数
def one_point_mutation(solution):
    # 这里只是示例，需要根据实际问题调整
    mutation_point = random.randint(0, len(solution) - 1)
    new_solution = solution.copy()
    new_solution[mutation_point] = random.randint(0, 9)
    return new_solution


# 根据低层次启发式向量LVa更新服务组合向量SVa，具体实现需根据问题定义
def update_sva(lva, sol):
    # 这里只是示例，需要根据实际问题调整
    for i in lva:
        for v in sol:
            s = [v[0], v[1], v[2]]
            if i == 0:
                s = A_swap_random_timeslots(v[0], v[1], v[2], v[5])
            elif i == 1:
                # s = A_reverse_consecutive_timeslots(v[0], v[1], v[2], v[5])
                s = B_night(v[0], v[1], v[2], v[5])
            elif i == 2:
                s = A_swap_classroom_type_timeslots(v[0], v[1], v[2], v[5])
            elif i == 3:
                s = A_random(v[0], v[1], v[2], v[5])
            elif i == 4:
                s = B_night(v[0], v[1], v[2], v[5])
            elif i == 5:
                s = B_course(v[0], v[1], v[2], v[5])
            elif i == 6:
                s = B_c_course(v[0], v[1], v[2], v[4], v[5])
            elif i == 7:
                s = B_c_teacher(v[0], v[1], v[2], v[3], v[5])
            elif i == 8:
                s = B_method(v[0], v[1], v[2], v[3], v[5])
            elif i == 9:
                pass

            s.append(v[3])
            s.append(v[4])
            s.append(v[5])
            v = s

    return sol


def A_swap_random_timeslots(schedule, class_schedule, teacher_schedule, schedule_all):
    # 找出使用过的教室的索引
    used_classroom_indices = []
    for classroom_index in range(len(schedule_all)):
        if any(schedule_all[classroom_index]):
            used_classroom_indices.append(classroom_index)

    # 随机选择两个不同的时间段
    # timeslot1, timeslot2 = random.sample(range(total_timeslots), 2)
    swap_list_1 = []
    for i in range(25):
        if i % 5 != 4:
            swap_list_1.append(i)
    swap_list_2 = [4, 9, 14, 19, 24]
    timeslot1 = random.choice(range(total_timeslots))
    if timeslot1 in swap_list_2:
        swap_list_2.remove(timeslot1)
        timeslot2 = random.choice(swap_list_2)
    else:
        swap_list_1.remove(timeslot1)
        timeslot2 = random.choice(swap_list_1)

    for used_cr in used_classroom_indices:
        if schedule[used_cr][timeslot1] and schedule[used_cr][timeslot2]:
            if check(used_cr, timeslot2, used_cr, timeslot1, schedule, class_schedule, teacher_schedule):
                schedule[used_cr][timeslot1], schedule[used_cr][timeslot2] = schedule[used_cr][timeslot2], \
                    schedule[used_cr][timeslot1]
                schedule_all[used_cr][timeslot1], schedule_all[used_cr][timeslot2] = schedule_all[used_cr][timeslot2], \
                    schedule_all[used_cr][timeslot1]
        elif schedule[used_cr][timeslot2] and schedule_all[used_cr][timeslot1] is None:
            if check(used_cr, timeslot1, used_cr, timeslot2, schedule, class_schedule, teacher_schedule):
                schedule[used_cr][timeslot1], schedule[used_cr][timeslot2] = schedule[used_cr][timeslot2], \
                    schedule[used_cr][timeslot1]
                schedule_all[used_cr][timeslot1], schedule_all[used_cr][timeslot2] = schedule_all[used_cr][timeslot2], \
                    schedule_all[used_cr][timeslot1]
        elif schedule[used_cr][timeslot1] and schedule_all[used_cr][timeslot2] is None:
            if check(used_cr, timeslot2, used_cr, timeslot1, schedule, class_schedule, teacher_schedule):
                schedule[used_cr][timeslot1], schedule[used_cr][timeslot2] = schedule[used_cr][timeslot2], \
                    schedule[used_cr][timeslot1]
                schedule_all[used_cr][timeslot1], schedule_all[used_cr][timeslot2] = schedule_all[used_cr][timeslot2], \
                    schedule_all[used_cr][timeslot1]

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

    # 获取所有教室类型
    classroom_types = list({classroom['type'] for classroom in classrooms})

    # 确保有可用的教室类型
    if not classroom_types:
        print("警告: 没有找到可用的教室类型")
        return [schedule, class_schedule, teacher_schedule]

    # 随机选择一种教室类型
    selected_type = random.choice(classroom_types)

    # 获取该类型教室在schedule中的索引
    type_indices = [i for i, classroom in enumerate(classrooms) if classroom['type'] == selected_type]

    # 确保该类型有教室
    if not type_indices:
        print(f"警告: 教室类型 {selected_type} 没有对应的教室")
        return [schedule, class_schedule, teacher_schedule]

    # 随机选择两个不同的时间段
    # timeslot1, timeslot2 = random.sample(range(total_timeslots), 2)
    swap_list_1 = []
    for i in range(25):
        if i % 5 != 4:
            swap_list_1.append(i)
    swap_list_2=[4,9,14,19,24]
    timeslot1 = random.choice(range(total_timeslots))
    if timeslot1 in swap_list_2:
        swap_list_2.remove(timeslot1)
        timeslot2=random.choice(swap_list_2)
    else:
        swap_list_1.remove(timeslot1)
        timeslot2=random.choice(swap_list_1)

    for used_cr in type_indices:
        if schedule[used_cr][timeslot1] and schedule[used_cr][timeslot2]:
            if check(used_cr, timeslot2, used_cr, timeslot1, schedule, class_schedule, teacher_schedule):
                schedule[used_cr][timeslot1], schedule[used_cr][timeslot2] = schedule[used_cr][timeslot2], \
                schedule[used_cr][timeslot1]
                schedule_all[used_cr][timeslot1], schedule_all[used_cr][timeslot2] = schedule_all[used_cr][timeslot2], \
                schedule_all[used_cr][timeslot1]
        elif schedule[used_cr][timeslot2] and schedule_all[used_cr][timeslot1] is None:
            if check(used_cr, timeslot1, used_cr, timeslot2, schedule, class_schedule, teacher_schedule):
                schedule[used_cr][timeslot1], schedule[used_cr][timeslot2] = schedule[used_cr][timeslot2], \
                schedule[used_cr][timeslot1]
                schedule_all[used_cr][timeslot1], schedule_all[used_cr][timeslot2] = schedule_all[used_cr][timeslot2], \
                schedule_all[used_cr][timeslot1]
        elif schedule[used_cr][timeslot1] and schedule_all[used_cr][timeslot2] is None:
            if check(used_cr, timeslot2, used_cr, timeslot1, schedule, class_schedule, teacher_schedule):
                schedule[used_cr][timeslot1], schedule[used_cr][timeslot2] = schedule[used_cr][timeslot2], \
                schedule[used_cr][timeslot1]
                schedule_all[used_cr][timeslot1], schedule_all[used_cr][timeslot2] = schedule_all[used_cr][timeslot2], \
                schedule_all[used_cr][timeslot1]

    # # 1. 更新班级和教师时间表
    # # 收集所有课程涉及的班级和教师
    # classes_involved = set()
    # teachers_involved = set()
    #
    # # 遍历该类型的所有教室
    # for classroom_idx in type_indices:
    #     # 处理时间段1的课程
    #     course1 = schedule[classroom_idx][timeslot1]
    #     if course1:
    #         classes_involved.update(course1['class'])
    #         teachers_involved.add(course1['teacher'])
    #
    #     # 处理时间段2的课程
    #     course2 = schedule[classroom_idx][timeslot2]
    #     if course2:
    #         classes_involved.update(course2['class'])
    #         teachers_involved.add(course2['teacher'])
    #
    # # 更新班级时间表：交换两个时间段的记录
    # for class_id in classes_involved:
    #     slots = class_schedule[class_id]
    #     has_slot1 = timeslot1 in slots
    #     has_slot2 = timeslot2 in slots
    #
    #     if has_slot1 and not has_slot2:
    #         slots.remove(timeslot1)
    #         slots.add(timeslot2)
    #     elif has_slot2 and not has_slot1:
    #         slots.remove(timeslot2)
    #         slots.add(timeslot1)
    #     elif has_slot1 and has_slot2:
    #         pass  # 两个时间段都有课，无需修改
    #     else:
    #         pass  # 两个时间段都没课，无需修改
    #
    # # 更新教师时间表：交换两个时间段的记录
    # for teacher_id in teachers_involved:
    #     slots = teacher_schedule[teacher_id]
    #     has_slot1 = timeslot1 in slots
    #     has_slot2 = timeslot2 in slots
    #
    #     if has_slot1 and not has_slot2:
    #         slots.remove(timeslot1)
    #         slots.add(timeslot2)
    #     elif has_slot2 and not has_slot1:
    #         slots.remove(timeslot2)
    #         slots.add(timeslot1)
    #     elif has_slot1 and has_slot2:
    #         pass  # 两个时间段都有课，无需修改
    #     else:
    #         pass  # 两个时间段都没课，无需修改
    #
    # # 2. 交换排课表中该类型教室的两个时间段
    # for classroom_idx in type_indices:
    #     schedule[classroom_idx][timeslot1], schedule[classroom_idx][timeslot2] = \
    #         schedule[classroom_idx][timeslot2], schedule[classroom_idx][timeslot1]
    #
    # # 3. 更新schedule_all中的对应记录
    # # 建立教室ID到schedule_all索引的映射
    # classroom_id_to_index = {classroom['id']: idx for idx, classroom in enumerate(classrooms)}
    #
    # # 对该类型的每个教室处理交换
    # for classroom_idx in type_indices:
    #     classroom_id = classrooms[classroom_idx]['id']
    #     if classroom_id in classroom_id_to_index:
    #         schedule_all_idx = classroom_id_to_index[classroom_id]
    #         # 交换schedule_all中的对应时间段
    #         schedule_all[schedule_all_idx][timeslot1], schedule_all[schedule_all_idx][timeslot2] = \
    #             schedule_all[schedule_all_idx][timeslot2], schedule_all[schedule_all_idx][timeslot1]

    return [schedule, class_schedule, teacher_schedule]


# 约束检查
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


def A_random(res, cr, tr, schedule_all):
    for x in range(1):
        count_dict = {}
        for index, r in enumerate(res):
            num = sum(1 for t in r if t)
            if num > 0:
                count_dict[index] = num

        # 根据使用次数排序，选择最少的5个
        sorted_items = sorted(count_dict.items(), key=lambda x: x[1])
        used_classroom_indices = [item[0] for item in sorted_items[:len(sorted_items)]]

        r1 = random.choice(used_classroom_indices)
        T1 = []
        for j in range(0, 25):
            if res[r1][j]:
                T1.append(j)
        t1 = random.choice(T1)

        used_classroom_indices1 = []
        for classroom_index in count_dict:
            if classrooms[classroom_index]['type'] in res[r1][t1]['allowed_classrooms']:
                used_classroom_indices1.append(classroom_index)

        T2 = [j for j in range(25)]
        sign = False
        while len(T2) > 0:
            t2 = random.choice(T2)
            R2 = copy.deepcopy(used_classroom_indices1)
            while len(R2) > 0:
                r2 = random.choice(R2)
                if (res[r2][t2] and (
                        res[r2][t2]['course'] != res[r1][t1]['course'] and classrooms[r1]['type'] in res[r2][t2][
                    'allowed_classrooms'])) or schedule_all[r2][t2] is None:
                    if check(r2, t2, r1, t1, res, cr, tr):
                        res[r1][t1], res[r2][t2] = res[r2][t2], res[r1][t1]
                        schedule_all[r1][t1], schedule_all[r2][t2] = schedule_all[r2][t2], schedule_all[r1][t1]
                        sign = True
                        break
                R2.remove(r2)
            if sign:
                break
            T2.remove(t2)
    return [res, cr, tr]


def B_night(res, cr, tr, schedule_all):
    for x in range(10):
        t1 = random.choice([4, 9, 14, 19, 24])
        r1 = 0
        V = 0
        for i in range(len(classrooms)):
            if res[i][t1] is not None and res[i][t1]['time'] * len(res[i][t1]['class']) > V:
                r1 = i
                V = res[i][t1]['time'] * len(res[i][t1]['class'])
        if res[r1][t1] is None:
            continue

        used_classroom_indices = []
        for classroom_index in range(len(res)):
            if any(res[classroom_index]) and classrooms[classroom_index]['type'] in res[r1][t1]['allowed_classrooms']:
                used_classroom_indices.append(classroom_index)

        T2 = [i for i in range(25) if i not in [4, 9, 14, 19, 24]]

        sign = False
        while len(T2) > 0:
            t2 = random.choice(T2)
            R2 = copy.deepcopy(used_classroom_indices)
            while len(R2) > 0:
                r2 = random.choice(R2)
                if (res[r2][t2] and res[r2][t2]['time'] * len(res[r2][t2]['class']) < V) or schedule_all[r2][
                    t2] is None:
                    if check(r2, t2, r1, t1, res, cr, tr):
                        res[r1][t1], res[r2][t2] = res[r2][t2], res[r1][t1]
                        schedule_all[r1][t1], schedule_all[r2][t2] = schedule_all[r2][t2], schedule_all[r1][t1]
                        sign = True
                        break
                R2.remove(r2)
            if sign:
                break
            T2.remove(t2)

    return [res, cr, tr]


def B_course(res, cr, tr, schedule_all):
    for x in range(10):
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
        if len(re_list) == 0:
            return [res, cr, tr]

        first = random.choice(re_list)
        r1, t1 = first[0], first[1]
        used_classroom_indices = []
        for classroom_index in range(len(res)):
            if any(res[classroom_index]) and classrooms[classroom_index]['type'] in res[r1][t1]['allowed_classrooms']:
                used_classroom_indices.append(classroom_index)

        T2 = [j for j in range(25)]
        sign = False
        while len(T2) > 0:
            t2 = random.choice(T2)
            R2 = copy.deepcopy(used_classroom_indices)
            while len(R2) > 0:
                r2 = random.choice(R2)
                if (res[r2][t2] and (
                        res[r2][t2]['course'] != res[r1][t1]['course'] and classrooms[r1]['type'] in res[r2][t2][
                    'allowed_classrooms'])) or schedule_all[r2][t2] is None:
                    if check(r2, t2, r1, t1, res, cr, tr):
                        res[r1][t1], res[r2][t2] = res[r2][t2], res[r1][t1]
                        schedule_all[r1][t1], schedule_all[r2][t2] = schedule_all[r2][t2], schedule_all[r1][t1]
                        sign = True
                        break
                R2.remove(r2)
            if sign:
                break
            T2.remove(t2)
    return [res, cr, tr]


def B_c_course(res, cr, tr,courses,schedule_all):

    for x in range(2):
        used_classroom_indices = []
        used_indices = []
        for i in range(len(res)):
            for j in range(0, 25):
                if res[i][j]:
                    used_indices.append([i, j])
                    used_classroom_indices.append(i)
        while True and len(used_indices)>0:
            u = random.choice(used_indices)
            r1,t1=u[0],u[1]
            used_classroom_indices1 = []
            for classroom_index in used_classroom_indices:
                if classrooms[classroom_index]['type'] in res[r1][t1]['allowed_classrooms']:
                    used_classroom_indices1.append(classroom_index)

            like_time = []
            for course in courses:
                if res[r1][t1]['course'] == course['name']:
                    if course['like'][t1 % 5] == -1:
                        for index, c in enumerate(course['like']):
                            if c == 1 or c == 0:
                                like_time.append(index)
                    elif course['like'][t1 % 5] == 0:
                        for index, c in enumerate(course['like']):
                            if c == 1:
                                like_time.append(index)
                    break
            if len(like_time) > 0:
                break
            used_indices.remove(u)


        T2 = [i for i in range(25) if i % 5 in like_time]
        sign = False
        while len(T2) > 0:
            t2 = random.choice(T2)
            R2=copy.deepcopy(used_classroom_indices1)
            while len(R2) > 0:
                r2 = random.choice(R2)
                if (res[r2][t2] and (
                        res[r2][t2]['course'] != res[r1][t1]['course'] and classrooms[r1]['type'] in res[r2][t2][
                    'allowed_classrooms'])) or schedule_all[r2][t2] is None:
                    if check(r2, t2, r1, t1, res, cr, tr):
                        res[r1][t1], res[r2][t2] = res[r2][t2], res[r1][t1]
                        schedule_all[r1][t1], schedule_all[r2][t2] = schedule_all[r2][t2], schedule_all[r1][t1]
                        sign = True
                        break
                R2.remove(r2)
            if sign:
                break
            T2.remove(t2)
    return [res, cr, tr]


def B_c_teacher(res, cr, tr,teachers,schedule_all):
    for x in range(2):
        used_classroom_indices = []
        used_indices = []
        for i in range(len(res)):
            for j in range(0, 25):
                if res[i][j]:
                    used_indices.append([i, j])
                    used_classroom_indices.append(i)

        while True and len(used_indices)>0:
            u = random.choice(used_indices)
            r1,t1=u[0],u[1]
            used_classroom_indices1 = []
            for classroom_index in used_classroom_indices:
                if classrooms[classroom_index]['type'] in res[r1][t1]['allowed_classrooms']:
                    used_classroom_indices1.append(classroom_index)

            like_time = []
            for teacher in teachers:
                if res[r1][t1]['teacher'] == teacher['name']:
                    if teacher['like1'][t1 // 5] == -1:
                        for index1, lt in enumerate(teacher['like1']):
                            if lt >= 0:
                                like_time.append(index1)

                    elif teacher['like1'][t1 // 5] == 0:
                        for index1, lt in enumerate(teacher['like1']):
                            if lt  >= 1:
                                like_time.append(index1)

                    break
            if len(like_time) > 0:
                break
            used_indices.remove(u)

        T2 = [i for i in range(25) if i // 5 in like_time]
        sign = False
        while len(T2) > 0:
            t2 = random.choice(T2)
            R2=copy.deepcopy(used_classroom_indices1)
            while len(R2) > 0:
                r2 = random.choice(R2)
                if (res[r2][t2] and (
                        res[r2][t2]['course'] != res[r1][t1]['course'] and classrooms[r1]['type'] in res[r2][t2][
                    'allowed_classrooms'])) or schedule_all[r2][t2] is None:
                    if check(r2, t2, r1, t1, res, cr, tr):
                        res[r1][t1], res[r2][t2] = res[r2][t2], res[r1][t1]
                        schedule_all[r1][t1], schedule_all[r2][t2] = schedule_all[r2][t2], schedule_all[r1][t1]
                        sign = True
                        break
                R2.remove(r2)
            if sign:
                break
            T2.remove(t2)
    return [res, cr, tr]


def B_method(res, cr, tr,teachers,schedule_all):
    used_classroom_indices = []
    pairs = [(0, 1), (2, 3), (5, 6), (7, 8), (10, 11), (12, 13), (15, 16), (17, 18), (20, 21), (22, 23)]
    for classroom_index in range(len(res)):
        if any(res[classroom_index]):
            used_classroom_indices.append(classroom_index)
    # print("cr:",used_classroom_indices)
    for x in range(10):
        M = random.choice(used_classroom_indices)
        used_classroom_time_indices = []
        for i in range(25):
            if res[M][i]:
                used_classroom_time_indices.append(i)
        if used_classroom_time_indices is None:
            continue
        while True and len(used_classroom_time_indices)>0:

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
            used_classroom_time_indices.remove(p1)

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

def c_classrooms(res_all):
    classrooms_num=0
    for index in range(0,len(res_all)):
        if any(res_all[index]):
            classrooms_num=classrooms_num+1
    return classrooms_num
# 计算适应度值
def c_obj_fun(paths, res):

    obj_value = 0  #教室目标函数计算
    for i, path in enumerate(paths):
        obj_value = obj_value + obj_func_all(res[i][0], path, res[i][2],c_classrooms(res[0][5]),len(paths))
    return obj_value/len(paths)

def nonlinear_decay_ao(iteration, concavity,linear_period,max_iterations,initial_ll,target_ll):
    """
    混合衰减函数：初期线性衰减，中期非线性凹函数快速衰减
    concavity参数控制凹度：值越小凹度越大，衰减越快
    """
    if iteration <= linear_period:
        # 初期线性衰减
        linear_ratio = iteration / max_iterations
        return initial_ll - (initial_ll - target_ll) * linear_ratio
    else:
        # 中期非线性凹函数衰减
        remaining_iterations = iteration - linear_period
        remaining_total = max_iterations - linear_period
        decay_ratio = remaining_iterations / remaining_total
        # 计算线性阶段结束时的值作为非线性阶段的初始值
        linear_end_value = initial_ll - (initial_ll - target_ll) * (linear_period / max_iterations)
        return linear_end_value - (linear_end_value - target_ll) * (decay_ratio ** concavity)


# 基于遗传和贪婪策略的超启发式算法
def GA_RG_HH(paths, max_iterations=10, population_size=5, crossover_rate=0.8, mutation_rate=0.2):
    print("GA_RG_HH生成初始解中...")
    population = [generate_initial_solution(paths) for _ in range(population_size)]
    print("GA_RG_HH生成完毕")
    best_fitness_per_iteration = []

    best_v = float('inf')
    fitness = np.full(population_size, np.inf)  # 初始适应度设为无穷大

    # 计算初始种群的适应度值，并更新全局最优
    for ind, pop in enumerate(population):
        obj_value = c_obj_fun(paths, pop[1:len(pop)])
        fitness[ind] = obj_value
        if obj_value < best_v:
            best_v = obj_value
            near_optimal_solution = copy.deepcopy(population[ind])

    print(fitness)
    print("GA_RG_HH初始最优解：", best_v)
    best_fitness_per_iteration.append(best_v)


    initial_ll = 10
    target_ll=1

    for iteration in range(max_iterations):
        new_population = []
        elite_solution = None
        elite_fitness = float('inf')

        # 记录当前精英解
        for i in range(population_size):
            if fitness[i] < elite_fitness:
                elite_fitness = fitness[i]
                elite_solution = copy.deepcopy(population[i])

        # 生成新种群（不计算适应度）
        for index in range(population_size - 1):  # 留出一个位置给精英
            # 选择操作
            solution_a, solution_b = selection(population, fitness)

            # 更新lva的长度
            # ll = initial_ll - (iteration // step)

            decay_ratio = iteration / max_iterations
            # # # 使用幂函数实现凹函数衰减，concavity控制凹度
            ll = initial_ll - (initial_ll - target_ll) * (decay_ratio)
            # ll = nonlinear_decay_ao(iteration,0.2,max_iterations/5,max_iterations,initial_ll,target_ll)

            solution_a[0] = solution_a[0][0:int(ll)]
            solution_b[0] = solution_b[0][0:int(ll)]
            lva = copy.deepcopy(solution_a[0])
            lva1 = copy.deepcopy(solution_b[0])

            if len(lva) != 1 and len(lva1) != 1:
                # 交叉操作
                if random.random() < crossover_rate and (len(lva) > 2 and len(lva1) > 2):
                    lva = two_point_crossover(lva, lva1)
                else:
                    lva = one_point_mutation(lva)
                # 变异操作
                if random.random() < mutation_rate:
                    lva = one_point_mutation(lva)
            else:
                lva[0] = random.randint(3, 8)
                # if iteration < 2 * max_iterations / 3:
                #     lva[0] = random.randint(3, 8)
                # else:
                #     lva[0] = 3

            # 生成新解（不计算适应度）
            sva = update_sva(lva, copy.deepcopy(solution_a[1:len(solution_a)]))
            sign = [lva]
            for new in sva:
                sign.append(new)
            new_population.append(sign)

        # 添加精英解
        new_population.append(elite_solution)

        # 统一计算适应度
        new_fitness = []
        for solution in new_population:
            new_v = c_obj_fun(paths, solution[1:])
            new_fitness.append(new_v)

        # 更新最佳解
        min_index = new_fitness.index(min(new_fitness))
        if new_fitness[min_index] < best_v:
            best_v = new_fitness[min_index]
            near_optimal_solution = copy.deepcopy(new_population[min_index])

        # 更新种群和适应度数组
        population = new_population
        fitness = new_fitness

        print("GA_RG_HH_iter:", iteration, ",best_v:", best_v, near_optimal_solution[0])
        best_fitness_per_iteration.append(best_v)

    # 记录适应度函数每个方向的值
    detail_nor = [0, 0, 0, 0, 0, 0, 0]
    detail_ori=[0, 0, 0, 0, 0, 0, 0]
    for i, path in enumerate(paths):
        de_nor,de_ori = obj_func_detail(near_optimal_solution[i + 1][0], path, c_classrooms(near_optimal_solution[i+1][5])
                             , near_optimal_solution[i + 1][2],len(paths))
        for j in range(len(detail_nor)):
            detail_nor[j] = detail_nor[j] + de_nor[j]
            detail_ori[j] = detail_ori[j] + de_ori[j]

    for i in range(len(detail_nor)):
        detail_nor[i] = detail_nor[i] / len(paths)
        detail_ori[i] = detail_ori[i] / len(paths)

    detail=detail_nor+detail_ori
    print(detail)
    return near_optimal_solution[1:len(near_optimal_solution)], best_v, best_fitness_per_iteration, detail


if __name__ == "__main__":
    paths = [
        r'data\large_new\data1_4.xlsx',
        r'data\large_new\data2.xlsx',
        # r'data\large_new\data3.xlsx',
        # r'data\large_new\data4.xlsx',
        # r'data\small_new\l_data01.xlsx',
    ]
    # paths = [
    #     r'data\small_new\l_data05.xlsx',
    # ]

    start = time.time()
    best_path, best_v, x, detail = GA_RG_HH(paths, 10)
    end = time.time()
    print("生成解的时间：", end - start)
    print("最短距离:", best_v)

    # for i, path in enumerate(paths):
    #     obj_func_all_print(best_path[i][0], path, c_classrooms(best_path[i][5]), best_path[i][2],len(paths))
    #
    # plot_schedule2(best_path[i][5], classrooms)
    # for i, path in enumerate(paths):
    #     plot_schedule(best_path[i][0], classrooms)
    #
    # plt.figure(figsize=(10, 6))
    # plt.plot(x, label='GA_RG_HH')
    #
    # plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    # plt.rcParams['axes.unicode_minus'] = False
    #
    # plt.title('不同算法的适应度值迭代过程')
    # plt.xlabel('迭代次数')
    # plt.ylabel('适应度值')
    # plt.legend()
    # plt.show()


