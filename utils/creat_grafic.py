import calendar

WORK_HOUR = 12
WORKER_STATUSES = {0: "8:00 - 20:00", 1: "10:00 - 22:00", 2: "day off"}

# приоритеты условий:
# 1. в каждой смене должен работать как минимум один работник
# 2. в месяц каждый работник работает не больше 12 смен (144 часа)
# 3. в пн на одного работника больше от средней нагрузки
# 4. в вс на одного работника меньше от средней нагрузки
# 5. если в сменах неравное кол-во человек, то в первой смене больше


def week_step(week_day):
    week_day += 1
    if week_day > 6:
        return 0
    else:
        return week_day


def create_worker_list_for_day(last_one, workers_in_day, w_count):
    def is_ok(next_one):
        if next_one >= w_count:
            return next_one-w_count
        return next_one
    return [is_ok(last_one+i) for i in range(1, workers_in_day+1)]


def create_grafic(workers, month, year):
    w_count = len(workers)
    able_work_day = w_count * WORK_HOUR
    days_in_month = calendar.monthrange(year, month)[1]
    need_work = days_in_month * 2

    first_week_day = calendar.monthrange(year, month)[0]
    tmp = first_week_day
    weed_days = []
    for i in range(days_in_month):
        if tmp == 0:
            need_work += 1
        elif tmp == 6:
            need_work -= 1
        if tmp > 6:
            tmp = 0
        weed_days.append(tmp)
        tmp = week_step(tmp)
    average_load = able_work_day // days_in_month
    if average_load == 0 and ((able_work_day / days_in_month) > 0):
        average_load = 1

    second_shift = average_load//2
    fisrt_shift = average_load - second_shift

    # сколько человек нужно на каждый жень недели в первую и вторую смену
    work_mask_week = {
                        0: [fisrt_shift + 1, second_shift],
                        1: [fisrt_shift, second_shift],
                        2: [fisrt_shift, second_shift],
                        3: [fisrt_shift, second_shift],
                        4: [fisrt_shift, second_shift],
                        5: [fisrt_shift, second_shift],
                        6: [fisrt_shift, second_shift - 1]
                      }

    # учет исключения, если средняя нагрузка на смену = 1, то в вс работаеют столько же человек
    if second_shift == 1:
        work_mask_week[6][1] = 1

    ans = [[worker]+[WORKER_STATUSES[2]]*days_in_month for worker in workers]
    worker_list = [-1]

    for day in range(1, days_in_month+1):
        week_day = weed_days[day-1]
        work_mask = work_mask_week[week_day]
        workers_in_day = sum(work_mask)
        worker_list = create_worker_list_for_day(worker_list[len(worker_list)-1], workers_in_day, w_count)
        for worker in worker_list[:work_mask[0]]:
            ans[worker][day] = WORKER_STATUSES[0]
        for worker in worker_list[work_mask[0]:]:
            ans[worker][day] = WORKER_STATUSES[1]

    # print("график работы для сотрудников создан")
    # for i in range(len(ans)):
    #     print(ans[i])
    # print("часов на каждого работника")
    # for i in range(len(ans)):
    #     count = 0
    #     for j in range(len(ans[i])):
    #         if ans[i][j] != "day off":
    #             count += 1
    #     print(ans[i][0], ":", count*12)

    return ans

