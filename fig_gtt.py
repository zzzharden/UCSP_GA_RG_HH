import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colorbar import ColorbarBase

total_weeks = 16
days_per_week = 5
timeslots_per_day = 5
total_timeslots = days_per_week * timeslots_per_day

def plot_schedule1(schedule,classrooms):
    # 找出使用过的教室的索引
    used_classroom_indices = []
    for classroom_index in range(len(schedule)):
        if any(schedule[classroom_index]):
            used_classroom_indices.append(classroom_index)

    # 收集所有课程 ID
    all_course_ids = set()
    for classroom in schedule:
        for timeslot in classroom:
            if timeslot and timeslot['id'] not in all_course_ids:
                all_course_ids.add(timeslot['id'])
    num_courses = len(all_course_ids)
    # 对课程 ID 进行排序
    sorted_course_ids = sorted(all_course_ids)

    # 自定义颜色映射，生成浅色且区分明显的颜色渐变
    num_colors = 100
    num_hue_segments = 12
    hue_step = 1 / num_hue_segments
    h_values = []
    s_values = []
    v_values = []
    for i in range(num_colors):
        hue_segment = i % num_hue_segments
        h = hue_segment * hue_step + np.random.uniform(0, hue_step)
        s = np.random.uniform(0.2, 0.6)
        v = np.random.uniform(0.65, 1)
        h_values.append(h)
        s_values.append(s)
        v_values.append(v)
    hsv_colors = np.column_stack((h_values, s_values, v_values))
    rgb_colors = np.array([mcolors.hsv_to_rgb(hsv) for hsv in hsv_colors])
    custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', rgb_colors)

    # 为每个课程 ID 分配颜色
    course_colors = {}
    for i, course_id in enumerate(sorted_course_ids):
        color = custom_cmap(i / num_courses)
        course_colors[course_id] = mcolors.to_hex(color)

    fig, ax = plt.subplots(figsize=(20, 9))
    total_timeslots = 25
    timeslots_per_day = 5
    days_per_week = 5

    for index, classroom_index in enumerate(used_classroom_indices):
        for timeslot in range(total_timeslots):
            course_info = schedule[classroom_index][timeslot]
            if course_info:
                course_id = course_info['id']
                ax.barh(index, 1, left=timeslot, height=1,color=course_colors.get(course_id, 'gray'),edgecolor='black',linewidth=0.7) #color=course_colors.get(course_id, 'gray')
                for i,x in enumerate(course_info['class']):
                    course_info['class'][i]=int(x)

                zzz=len(course_info['class'])
                if zzz==1:
                    ax.text(timeslot, index,
                            f"course:{course_info['course']}\nclass:{course_info['class'][0]}\nteacher:{course_info['teacher']}\nweek:1-{course_info['time']}",
                            ha='left', va='center', fontsize=8.8)
                elif zzz==2:
                    ax.text(timeslot, index,
                            f"course:{course_info['course']}\nclass:{course_info['class'][0]},{course_info['class'][1]}\nteacher:{course_info['teacher']}\nweek:1-{course_info['time']}",
                            ha='left', va='center', fontsize=8.8)

                elif zzz==3:
                    ax.text(timeslot, index,
                            f"course:{course_info['course']}\nclass:{course_info['class'][0]},{course_info['class'][1]}\n{course_info['class'][2]}\nteacher:{course_info['teacher']}\nweek:1-{course_info['time']}",
                            ha='left', va='center', fontsize=8.8)
                elif zzz==4:
                    ax.text(timeslot, index,
                            f"course:{course_info['course']}\nclass:{course_info['class'][0]},{course_info['class'][1]}\n{course_info['class'][2]},{course_info['class'][3]}\nteacher:{course_info['teacher']}\nweek:1-{course_info['time']}",
                            ha='left', va='center', fontsize=8.8)

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    ax.set_xlabel('timeslots(5 weekdays/week, 5 periods/weekday)', fontsize=14)
    ax.set_ylabel('classrooms(type_number)', fontsize=14)
    ax.set_yticks(np.arange(len(used_classroom_indices)))
    ax.set_yticklabels([classrooms[i]['id'] for i in used_classroom_indices], fontsize=12)
    ax.set_title('Instance8(classrooms--timeslots)', fontsize=14)

    xticks = [0]
    xticklabels = ['0']
    for i in range(0, timeslots_per_day * days_per_week):
        d_num = i // 5 + 1
        p_num = i % 5 + 1
        xticks.append(i + 1)
        if p_num == 5:
            xticklabels.append(f"P{p_num}\nD{d_num}")
        else:
            xticklabels.append(f"P{p_num}")

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, fontsize=12)

    # 调整坐标轴范围
    ax.set_xlim(left=0, right=total_timeslots)
    # 减小空白
    plt.margins(x=0, y=0)

    # 添加颜色渐变条作为图例
    norm = mcolors.Normalize(vmin=0, vmax=num_courses - 1)
    # 计算颜色渐变条的位置和大小
    cax = fig.add_axes([0.05, 0.08, 0.92, 0.03])  # 调整颜色渐变条的位置和大小
    cb = ColorbarBase(cax, cmap=custom_cmap, norm=norm, orientation='horizontal')
    tick_positions = np.linspace(0, num_courses - 1, 10, dtype=int)  # 调整刻度数量
    cb.set_ticks(tick_positions)
    cb.set_ticklabels([sorted_course_ids[i] for i in tick_positions])

    plt.tight_layout()
    # 增大 bottom 参数的值来扩宽 x 轴到底部的空白距离
    plt.subplots_adjust(bottom=0.2)

    #plt.savefig('little_gtt.svg')

    plt.show()

def plot_schedule2(schedule, classrooms):
    # 找出使用过的教室的索引
    used_classroom_indices = []
    for classroom_index in range(len(schedule)):
        if any(schedule[classroom_index]):
            used_classroom_indices.append(classroom_index)

    # 收集所有课程 ID
    all_course_ids = set()
    for classroom in schedule:
        for timeslot in classroom:
            if timeslot:
                all_course_ids.add(timeslot['id'])
    num_courses = len(all_course_ids)
    # 对课程 ID 进行排序
    sorted_course_ids = sorted(all_course_ids)

    # 自定义颜色映射，生成浅色且区分明显的颜色渐变
    num_colors = 1111
    num_hue_segments = 12
    hue_step = 1 / num_hue_segments
    h_values = []
    s_values = []
    v_values = []
    for i in range(num_colors):
        hue_segment = i % num_hue_segments
        h = hue_segment * hue_step + np.random.uniform(0, hue_step)
        s = np.random.uniform(0.2, 0.6)
        v = np.random.uniform(0.65, 1)
        h_values.append(h)
        s_values.append(s)
        v_values.append(v)
    hsv_colors = np.column_stack((h_values, s_values, v_values))
    rgb_colors = np.array([mcolors.hsv_to_rgb(hsv) for hsv in hsv_colors])
    custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', rgb_colors)

    # 为每个课程 ID 分配颜色
    course_colors = {}
    for i, course_id in enumerate(sorted_course_ids):
        color = custom_cmap(i / num_courses)
        course_colors[course_id] = mcolors.to_hex(color)

    fig, ax = plt.subplots(figsize=(20, 12))
    total_timeslots = 25
    timeslots_per_day = 5
    days_per_week = 5

    for index, classroom_index in enumerate(used_classroom_indices):
        for timeslot in range(total_timeslots):
            course_info = schedule[classroom_index][timeslot]
            if course_info:
                course_id = course_info['id']
                ax.barh(index, 1, left=timeslot, height=1, color=course_colors[course_id],edgecolor='black',linewidth=0.5)
                ax.text(timeslot, index, f"{course_id}:1-{course_info['time']}",
                        ha='left', va='center', fontsize=7.2)

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    ax.set_xlabel('timeslots(5 weekdays/week, 5 periods/weekday)', fontsize=14)
    ax.set_ylabel('classrooms(type_number)', fontsize=14)
    ax.set_yticks(np.arange(len(used_classroom_indices)))
    ax.set_yticklabels([classrooms[i]['id'] for i in used_classroom_indices], fontsize=10)
    ax.set_title('Instance14(classrooms--timeslots)', fontsize=14)

    xticks = [0]
    xticklabels = ['0']
    for i in range(0, timeslots_per_day * days_per_week):
        d_num = i // 5 + 1
        p_num = i % 5 + 1
        xticks.append(i + 1)
        if p_num == 5:
            xticklabels.append(f"P{p_num}\nD{d_num}")
        else:
            xticklabels.append(f"P{p_num}")

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, fontsize=8)

    # 调整坐标轴范围
    ax.set_xlim(left=0, right=total_timeslots)

    # 减小空白
    plt.margins(x=0, y=0)

    # # 添加颜色渐变条作为图例
    # norm = mcolors.Normalize(vmin=0, vmax=num_courses - 1)
    # # 计算颜色渐变条的位置和大小
    # cax = fig.add_axes([0.05, 0.08, 0.92, 0.03])  # 调整颜色渐变条的位置和大小
    # cb = ColorbarBase(cax, cmap=custom_cmap, norm=norm, orientation='horizontal')
    # tick_positions = np.linspace(0, num_courses - 1, 15, dtype=int)  # 调整刻度数量
    # cb.set_ticks(tick_positions)
    # cb.set_ticklabels([sorted_course_ids[i] for i in tick_positions])

    plt.tight_layout()
    # 增大 bottom 参数的值来扩宽 x 轴到底部的空白距离
    # plt.subplots_adjust(bottom=0.2)

    plt.savefig('cosine_wave3.svg')

    plt.show()
# def plot_schedule1(schedule, classrooms):
#     # 找出使用过的教室的索引
#     used_classroom_indices = []
#     for classroom_index in range(len(schedule)):
#         if any(schedule[classroom_index]):
#             used_classroom_indices.append(classroom_index)
#
#     total_timeslots = 25
#     timeslots_per_day = 5
#     days_per_week = 5
#
#     # 创建表格数据
#     table_data = []
#     for classroom_index in used_classroom_indices:
#         row = []
#         for timeslot in range(total_timeslots):
#             course_info = schedule[classroom_index][timeslot]
#             if course_info:
#                 course_str = f"CT: {course_info['course']}\n"
#                 class_str = "CS: " + ", ".join(map(str, course_info['class'])) + "\n"
#                 teacher_str = f"TC: {course_info['teacher']}\n"
#                 week_str = f"W: 1-{course_info['time']}"
#                 cell_text = course_str + class_str + teacher_str + week_str
#             else:
#                 cell_text = ""
#             row.append(cell_text)
#         table_data.append(row)
#
#     plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
#     plt.rcParams['axes.unicode_minus'] = False
#
#     fig, ax = plt.subplots(figsize=(20, 10))
#     ax.axis('off')
#
#     # 创建表格
#     table = ax.table(cellText=table_data,
#                      rowLabels=[classrooms[i]['id'] for i in used_classroom_indices],
#                      colLabels=[f"P{(i % 5) + 1}\nD{(i // 5) + 1}" for i in range(total_timeslots)],
#                      loc='center')
#
#     table.auto_set_font_size(False)
#     table.set_fontsize(8)
#     table.scale(1.5, 3)
#
#     plt.title('课程安排表格')
#     plt.tight_layout()
#     plt.savefig('schedule_table.svg')
#     plt.show()
# def plot_schedule_excel(schedule, classrooms):
#     # 找出使用过的教室的索引
#     used_classroom_indices = []
#     for classroom_index in range(len(schedule)):
#         if any(schedule[classroom_index]):
#             used_classroom_indices.append(classroom_index)
#
#     total_timeslots = 25
#     timeslots_per_day = 5
#     days_per_week = 5
#
#     # 创建表格数据
#     table_data = []
#     for classroom_index in used_classroom_indices:
#         row = []
#         for timeslot in range(total_timeslots):
#             course_info = schedule[classroom_index][timeslot]
#             if course_info:
#                 course_str = f"CT: {course_info['course']}\n"
#                 class_str = "CS: " + ", ".join(map(str, course_info['class'])) + "\n"
#                 teacher_str = f"TC: {course_info['teacher']}\n"
#                 week_str = f"W: 1-{course_info['time']}"
#                 cell_text = course_str + class_str + teacher_str + week_str
#             else:
#                 cell_text = ""
#             row.append(cell_text)
#         table_data.append(row)
#
#     # 创建 DataFrame
#     df = pd.DataFrame(table_data,
#                       index=[classrooms[i]['id'] for i in used_classroom_indices],
#                       columns=[f"P{(i % 5) + 1}\nD{(i // 5) + 1}" for i in range(total_timeslots)])
#
#     # 保存到 Excel 文件
#     df.to_excel('schedule_table_little.xlsx')

def plot_schedule(schedule, classrooms):
    # 找出使用过的教室的索引
    used_classroom_indices = []
    for classroom_index in range(len(schedule)):
        if any(schedule[classroom_index]):
            used_classroom_indices.append(classroom_index)

    # 收集所有课程 ID
    all_course_ids = set()
    for classroom in schedule:
        for timeslot in classroom:
            if timeslot:
                all_course_ids.add(timeslot['id'])
    num_courses = len(all_course_ids)
    # 对课程 ID 进行排序
    sorted_course_ids = sorted(all_course_ids)

    # 自定义颜色映射，生成浅色且区分明显的颜色渐变
    num_colors = 243
    num_hue_segments = 12
    hue_step = 1 / num_hue_segments
    h_values = []
    s_values = []
    v_values = []
    for i in range(num_colors):
        hue_segment = i % num_hue_segments
        h = hue_segment * hue_step + np.random.uniform(0, hue_step)
        s = np.random.uniform(0.2, 0.6)
        v = np.random.uniform(0.65, 1)
        h_values.append(h)
        s_values.append(s)
        v_values.append(v)
    hsv_colors = np.column_stack((h_values, s_values, v_values))
    rgb_colors = np.array([mcolors.hsv_to_rgb(hsv) for hsv in hsv_colors])
    custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', rgb_colors)

    # 为每个课程 ID 分配颜色
    course_colors = {}
    for i, course_id in enumerate(sorted_course_ids):
        color = custom_cmap(i / num_courses)
        course_colors[course_id] = mcolors.to_hex(color)

    fig, ax = plt.subplots(figsize=(20, 12))
    total_timeslots = 25
    timeslots_per_day = 5
    days_per_week = 5

    for index, classroom_index in enumerate(used_classroom_indices):
        for timeslot in range(total_timeslots):
            course_info = schedule[classroom_index][timeslot]
            if course_info:
                course_id = course_info['id']
                ax.barh(index, 1, left=timeslot, height=1, color=course_colors[course_id],edgecolor='black',linewidth=0.7)
                ax.text(timeslot, index, f"{course_id}:1-{course_info['time']}",
                        ha='left', va='center', fontsize=10)

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    ax.set_xlabel('timeslots(5 weekdays/week, 5 periods/weekday)', fontsize=14)
    ax.set_ylabel('classrooms(type_number)', fontsize=14)
    ax.set_yticks(np.arange(len(used_classroom_indices)))
    ax.set_yticklabels([classrooms[i]['id'] for i in used_classroom_indices], fontsize=10)
    ax.set_title('Instance11(classrooms--timeslots)', fontsize=14)

    xticks = [0]
    xticklabels = ['0']
    for i in range(0, timeslots_per_day * days_per_week):
        d_num = i // 5 + 1
        p_num = i % 5 + 1
        xticks.append(i + 1)
        if p_num == 5:
            xticklabels.append(f"P{p_num}\nD{d_num}")
        else:
            xticklabels.append(f"P{p_num}")

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, fontsize=8)

    # 调整坐标轴范围
    ax.set_xlim(left=0, right=total_timeslots)

    # 减小空白
    plt.margins(x=0, y=0)

    # # 添加颜色渐变条作为图例
    # norm = mcolors.Normalize(vmin=0, vmax=num_courses - 1)
    # # 计算颜色渐变条的位置和大小
    # cax = fig.add_axes([0.05, 0.08, 0.92, 0.03])  # 调整颜色渐变条的位置和大小
    # cb = ColorbarBase(cax, cmap=custom_cmap, norm=norm, orientation='horizontal')
    # tick_positions = np.linspace(0, num_courses - 1, 15, dtype=int)  # 调整刻度数量
    # cb.set_ticks(tick_positions)
    # cb.set_ticklabels([sorted_course_ids[i] for i in tick_positions])

    plt.tight_layout()
    # 增大 bottom 参数的值来扩宽 x 轴到底部的空白距离
    plt.subplots_adjust(bottom=0.2)

    #plt.savefig('cosine_wave3.svg')

    plt.show()


def save_schedule_to_excel(schedule, classrooms):
    total_timeslots = 25
    # 找出使用过的教室的索引
    used_classroom_indices = []
    for classroom_index in range(len(schedule)):
        if any(schedule[classroom_index]):
            used_classroom_indices.append(classroom_index)

    # 创建一个以使用过的教室 ID 为索引，时间段为列名的空 DataFrame，并初始化为 0
    columns = [f"{i+1}" for i in range(total_timeslots)]
    index = [classrooms[i]['id'] for i in used_classroom_indices]
    df = pd.DataFrame(0, index=index, columns=columns)

    # 填充 DataFrame 中的课程信息
    for classroom_index in used_classroom_indices:
        for timeslot in range(total_timeslots):
            course_info = schedule[classroom_index][timeslot]
            if course_info:
                df.loc[classrooms[classroom_index]['id'], f"{timeslot+1}"] = f"{course_info['id']},{course_info['time']}"

    # 将 DataFrame 保存为 Excel 文件
    df.to_excel('gantt_chart_data.xlsx')


def plot_teacher_schedule(schedule):
    # 找出有排课的教师
    used_teachers = []
    teacher_schedule = {}
    for classroom_schedule in schedule:
        for period,timeslot_info in enumerate(classroom_schedule):
            if timeslot_info:
                teacher = timeslot_info['teacher']
                if teacher not in used_teachers:
                    used_teachers.append(teacher)
                if teacher not in teacher_schedule:
                    teacher_schedule[teacher] = [None] * total_timeslots
                teacher_schedule[teacher][period] = timeslot_info

    color_map = plt.cm.get_cmap("tab20")
    # 用于存储 id 到颜色的映射
    course_colors = {}
    color_index = 0

    fig, ax = plt.subplots(figsize=(15, 18))

    for index, teacher in enumerate(used_teachers):
        for timeslot in range(total_timeslots):
            course_info = teacher_schedule[teacher][timeslot]
            if course_info:
                course_id = course_info['id']
                if course_id not in course_colors:
                    # 如果 id 不在颜色映射中，分配一个新的颜色
                    course_colors[course_id] = mcolors.to_hex(color_map(color_index % 20))
                    color_index += 1
                ax.barh(index, 1, left=timeslot, height=1, color=course_colors.get(course_id, 'gray'))
                ax.text(timeslot, index, f"{course_info['id']}:1-{course_info['time']}",
                        ha='left', va='center', fontsize=8)

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    ax.set_xlabel('时间段')
    ax.set_ylabel('教师')
    ax.set_yticks(np.arange(len(used_teachers)))
    ax.set_yticklabels(used_teachers)
    ax.set_title('教师课程安排甘特图')

    xticks = [0]
    xticklabels = ['0']
    for i in range(0, timeslots_per_day * days_per_week):
        d_num = i // 5 + 1
        p_num = i % 5 + 1
        xticks.append(i + 1)
        if p_num == 5:
            xticklabels.append(f"P{p_num}\nD{d_num}")
        else:
            xticklabels.append(f"P{p_num}")

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    plt.tight_layout()

    # plt.savefig('teacher_schedule.svg')

    plt.show()


def plot_class_schedule(schedule,classrooms):
    # 找出有排课的班级
    used_classes = []
    class_schedule = {}
    for classroom_schedule in schedule:
        for period,timeslot_info in enumerate(classroom_schedule):
            if timeslot_info:
                for class_id in timeslot_info['class']:
                    if class_id not in used_classes:
                        used_classes.append(class_id)
                    if class_id not in class_schedule:
                        class_schedule[class_id] = [None] * total_timeslots
                    class_schedule[class_id][period] = timeslot_info
    # 收集所有课程 ID
    all_course_ids = set()
    for classroom in schedule:
        for timeslot in classroom:
            if timeslot:
                all_course_ids.add(timeslot['id'])
    num_courses = len(all_course_ids)
    # 对课程 ID 进行排序
    sorted_course_ids = sorted(all_course_ids)

    # 自定义颜色映射，生成浅色且区分明显的颜色渐变
    num_colors = 243
    num_hue_segments = 12
    hue_step = 1 / num_hue_segments
    h_values = []
    s_values = []
    v_values = []
    for i in range(num_colors):
        hue_segment = i % num_hue_segments
        h = hue_segment * hue_step + np.random.uniform(0, hue_step)
        s = np.random.uniform(0.2, 0.6)
        v = np.random.uniform(0.65, 1)
        h_values.append(h)
        s_values.append(s)
        v_values.append(v)
    hsv_colors = np.column_stack((h_values, s_values, v_values))
    rgb_colors = np.array([mcolors.hsv_to_rgb(hsv) for hsv in hsv_colors])
    custom_cmap = LinearSegmentedColormap.from_list('custom_cmap', rgb_colors)

    # 为每个课程 ID 分配颜色
    course_colors = {}
    for i, course_id in enumerate(sorted_course_ids):
        color = custom_cmap(i / num_courses)
        course_colors[course_id] = mcolors.to_hex(color)

    fig, ax = plt.subplots(figsize=(20, 10))

    for index, classroom_index in enumerate(used_classes):
        for timeslot in range(total_timeslots):
            course_info = class_schedule[classroom_index][timeslot]
            if course_info:
                course_id = course_info['id']
                ax.barh(index, 1, left=timeslot, height=1, color=course_colors[course_id], edgecolor='black',
                        linewidth=0.7)
                ax.text(timeslot, index, f"{course_id}:1-{course_info['time']}",
                        ha='left', va='center', fontsize=10)

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    ax.set_xlabel('timeslots(5 weekdays/week, 5 periods/weekday)', fontsize=14)
    ax.set_ylabel('classes(grade_major_number)', fontsize=14)
    ax.set_yticks(np.arange(len(used_classes)))
    ax.set_yticklabels(used_classes, fontsize=10)
    ax.set_title('Instance11(classes--timeslots)', fontsize=14)

    xticks = [0]
    xticklabels = ['0']
    for i in range(0, timeslots_per_day * days_per_week):
        d_num = i // 5 + 1
        p_num = i % 5 + 1
        xticks.append(i + 1)
        if p_num == 5:
            xticklabels.append(f"P{p_num}\nD{d_num}")
        else:
            xticklabels.append(f"P{p_num}")

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, fontsize=8)

    # 调整坐标轴范围
    ax.set_xlim(left=0, right=total_timeslots)

    # 减小空白
    plt.margins(x=0, y=0)

    # 添加颜色渐变条作为图例
    norm = mcolors.Normalize(vmin=0, vmax=num_courses - 1)
    # 计算颜色渐变条的位置和大小
    cax = fig.add_axes([0.05, 0.08, 0.92, 0.03])  # 调整颜色渐变条的位置和大小
    cb = ColorbarBase(cax, cmap=custom_cmap, norm=norm, orientation='horizontal')
    tick_positions = np.linspace(0, num_courses - 1, 15, dtype=int)  # 调整刻度数量
    cb.set_ticks(tick_positions)
    cb.set_ticklabels([sorted_course_ids[i] for i in tick_positions])

    plt.tight_layout()
    # 增大 bottom 参数的值来扩宽 x 轴到底部的空白距离
    plt.subplots_adjust(bottom=0.2)

    plt.savefig('cosine_wave2.svg')

    plt.show()





def plot_course_schedule(schedule):
    # 找出所有课程及其对应的排课信息
    course_schedule = {}
    for classroom_schedule in schedule:
        for period,timeslot_info in enumerate(classroom_schedule):
            if timeslot_info:
                course_id = timeslot_info['id']
                if course_id not in course_schedule:
                    course_schedule[course_id] = []
                course_schedule[course_id].append(period)
    # 获取所有课程的 ID 并排序
    used_courses = sorted(course_schedule.keys())

    color_map = plt.cm.get_cmap("tab20")
    # 用于存储 id 到颜色的映射
    course_colors = {}
    color_index = 0

    fig, ax = plt.subplots(figsize=(15, 15))

    for index, course_id in enumerate(used_courses):
        course_timeslots = course_schedule[course_id]
        if course_id not in course_colors:
            # 如果 id 不在颜色映射中，分配一个新的颜色
            course_colors[course_id] = mcolors.to_hex(color_map(color_index % 20))
            color_index += 1
        for timeslot in course_timeslots:
            ax.barh(index, 1, left=timeslot, height=1, color=course_colors.get(course_id, 'gray'))
            ax.text(timeslot, index, f"{course_id}:1-{timeslot + 1}",
                    ha='left', va='center', fontsize=8)

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

    ax.set_xlabel('时间段')
    ax.set_ylabel('课程')
    ax.set_yticks(np.arange(len(used_courses)))
    ax.set_yticklabels(used_courses)
    ax.set_title('课程安排甘特图')

    xticks = [0]
    xticklabels = ['0']
    for i in range(0, timeslots_per_day * days_per_week):
        d_num = i // 5 + 1
        p_num = i % 5 + 1
        xticks.append(i + 1)
        if p_num == 5:
            xticklabels.append(f"P{p_num}\nD{d_num}")
        else:
            xticklabels.append(f"P{p_num}")

    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)

    plt.tight_layout()

    plt.savefig('course_schedule.svg')

    plt.show()


def plot_teacher_heatmap(schedule, teachers):
    # 获取所有教师的名字
    teacher_names = [teacher['name'] for teacher in teachers]
    # 初始化教师每天课程数量的统计矩阵
    teacher_day_course_count = np.zeros((len(teacher_names), days_per_week))

    # 统计每个教师每天的课程数量
    for classroom_schedule in schedule:
        for period,timeslot_info in enumerate(classroom_schedule):
            if timeslot_info:
                teacher_name = timeslot_info['teacher']
                teacher_index = teacher_names.index(teacher_name)
                timeslot = period
                day = timeslot // timeslots_per_day
                teacher_day_course_count[teacher_index, day] += 1

    # 过滤掉 5 天都没课的教师
    total_courses_per_teacher = teacher_day_course_count.sum(axis=1)
    active_teacher_indices = np.where(total_courses_per_teacher > 0)[0]
    active_teacher_names = [teacher_names[i] for i in active_teacher_indices]
    active_teacher_day_course_count = teacher_day_course_count[active_teacher_indices]

    # 绘制热力图
    plt.figure(figsize=(10, 15))
    sns.heatmap(active_teacher_day_course_count, annot=True, fmt=".0f", cmap="YlGnBu",
                xticklabels=[f"Day {i + 1}" for i in range(days_per_week)],
                yticklabels=active_teacher_names)
    plt.xlabel('Day')
    plt.ylabel('Teacher')
    plt.title('Teacher - Day Course Heatmap')
    plt.tight_layout()
    plt.show()

def plot_class_heatmap(schedule, classes):
    # 初始化班级每天课程数量的统计矩阵
    class_day_course_count = np.zeros((len(classes), days_per_week))

    # 统计每个班级每天的课程数量
    for classroom_schedule in schedule:
        for period,timeslot_info in enumerate(classroom_schedule):
            if timeslot_info:
                for class_id in timeslot_info['class']:

                    class_index = classes.index(class_id)
                    timeslot = period
                    day = timeslot // timeslots_per_day
                    class_day_course_count[class_index, day] += 1

    # 绘制热力图
    plt.figure(figsize=(10, 10))
    sns.heatmap(class_day_course_count, annot=True, fmt=".0f", cmap="YlGnBu",
                xticklabels=[f"Day {i + 1}" for i in range(days_per_week)],
                yticklabels=classes)
    plt.xlabel('Day')
    plt.ylabel('Class')
    plt.title('Class - Day Course Heatmap')
    plt.tight_layout()
    plt.show()

def generate_class_schedules(schedule,classrooms,classes):
    class_schedules = {class_id: [[''] * timeslots_per_day for _ in range(days_per_week)] for class_id in classes}
    for classroom_index in range(len(schedule)):
        for timeslot in range(total_timeslots):
            course_info = schedule[classroom_index][timeslot]
            if course_info:
                for class_id in course_info['class']:
                    day = timeslot // timeslots_per_day
                    time = timeslot % timeslots_per_day
                    class_schedules[class_id][day][time] = f"C: {course_info['course']}\nT: {course_info['teacher']}\nR: {classrooms[classroom_index]['id']}\nDW: {course_info['time']}"
    return class_schedules

def visualize_class_schedules(class_schedules):
    days = ['周一', '周二', '周三', '周四', '周五']
    time = ['上午1','上午2','下午1','下午2','晚上']
    times = [f'第{i + 1} 段' for i in range(timeslots_per_day)]

    for class_id, class_schedule in class_schedules.items():
        # 创建一个空的表格数据
        table_data = []
        table_data.append([''] + days)  # 第一行添加表头

        # 逐行添加课程信息
        for i in range(len(times)):
            row = [times[i]] + class_schedule[i]
            table_data.append(row)

        # 创建一个图形和轴
        fig, ax = plt.subplots(figsize=(8, 7))

        # 隐藏坐标轴
        ax.axis('off')

        # 创建表格
        table = ax.table(cellText=table_data, loc='center')

        # 设置表格字体和大小
        table.set_fontsize(10)
        table.scale(1, 5)

        # 设置表格标题
        ax.set_title(f'班级 {class_id} 课表')

        # 遍历表格中的每个单元格，将文字居中显示
        for key, cell in table.get_celld().items():
            cell.set_text_props(ha='center', va='center')

        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['axes.unicode_minus'] = False
        # 显示图形
        plt.show()

def generate_excel_schedule(res, classrooms, classes,name):
    total_timeslots = 25
    # 创建一个空的 DataFrame，列名为时间段，索引为班级
    df = pd.DataFrame(index=classes, columns=range(total_timeslots))

    for classroom_index, timeslot_schedule in enumerate(res):
        classroom = classrooms[classroom_index]['id']
        for timeslot, course_info in enumerate(timeslot_schedule):
            if course_info is not None:
                course = course_info['course']
                teacher = course_info['teacher']
                time = course_info['time']
                for class_id in course_info['class']:
                    df.at[class_id, timeslot] =  f"{course}\n{teacher}\n{classroom}\n{time}"
    df.to_excel(name+'.xlsx')

    return df