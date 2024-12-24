# Импортируем необходимые библиотеки.
import krpc
import time
import json
import concurrent.futures as cf
import numpy as np

conn = krpc.connect(name="The Loop")  # Соединение с KSP.
vessel = conn.space_center.active_vessel  # Инициализация переменной, отвечающей за взаимодействие с ЛА.
ref_frame = vessel.orbit.body.reference_frame  # Инициализация переменной, предоставляющей систему отсчета для положений, вращений и скоростей.
vessel.control.sas = False  # Отключение модуля SAS.

# Инициализируем переменные:
target_start_speed = 80  # Целевая скорость самолета при разгоне (м/с).
target_turn_speed = 195  # Целевая скорость самолета перед разворотом (м/с).
target_final_speed = 250  # Целевая скорость самолета перед выполнением маневра (м/с).
target_pitch_up = 15  # Целевой угол наклона самолета при взлете (°).
target_pitch_down = -1  # Целевой угол наклона самолета при посадке (°).
target_altitude = 1000  # Целевая высота, на которой оканчивается этап взлета самолета (м).
horizontal_pitch = 0  # Целевой Курс самолета по оси Ox относительно горизонта (°).

# Инициализируем переменные-флаги:
finish = False
in_loop = False

# Инициализируем словарь, в дальнейшем использующийся для записи данных всего полета по ключам.
flight_data = {
    "t": [],  # Время (с).
    "x_kerbin": [],  # Координата по оси Ox относительно центра планеты Kerbin ЛА (м).
    "y_kerbin": [],  # Координата по оси Oy относительно центра планеты Kerbin ЛА (м).
    "x_start": [],  # Координата по оси Ox относительно стартовой позиции (взлетной полосы) ЛА (м).
    "y_start": [],  # Координата по оси Oy относительно стартовой позиции (взлетной полосы) ЛА (м).
    "v": [],  # Общая скорость ЛА (м/с).
    "overload": [],  # Перегрузка (G).
    "angle": [],  # Угол (°).
    "v_x": [],  # Общая скорость ЛА по оси Ox (м/с).
    "v_y": []  # Общая скорость ЛА по оси Oy (м/с).
}

# Инициализируем словарь, в дальнейшем использующийся для записи данных мертвой петли по ключам.
flight_loop_data = {
    "t": [],  # Время (с).
    "x_kerbin": [],  # Координата по оси Ox относительно центра планеты Kerbin ЛА (м).
    "y_kerbin": [],  # Координата по оси Oy относительно центра планеты Kerbin ЛА (м).
    "x_start": [],  # Координата по оси Ox относительно стартовой позиции (взлетной полосы) ЛА (м).
    "y_start": [],  # Координата по оси Oy относительно стартовой позиции (взлетной полосы) ЛА (м).
    "v": [],  # Общая скорость ЛА (м/с).
    "overload": [],  # Перегрузка (G).
    "angle": [],  # Угол (°).
    "v_x": [],  # Общая скорость ЛА по оси Ox (м/с).
    "v_y": []  # Общая скорость ЛА по оси Oy (м/с).
}

# Инициализируем словарь, в дальнейшем использующийся для записи стартовых данных для математической модели по ключам.
start_data = {
    "a_x": 0,  # Стартовое общее ускорение ЛА по оси Ox (м/с²).
    "a_y": 0,  # Стартовое общее ускорение ЛА по оси Oy (м/с²).
    "v_x": 0,  # Стартовая общая скорость ЛА по оси Ox (м/с).
    "v_y": 0  # Стартовая общая скорость ЛА по оси Oy (м/с).
}


# Функция, записывающая данные во время всего полета и петли в словари.
def collect_data() -> None:
    x0 = vessel.position(ref_frame)[0]
    start_mean_altitude = int(vessel.flight().mean_altitude)

    while not finish:
        flight_data["x_kerbin"].append(round(vessel.position(ref_frame)[0], 3))
        flight_data["y_kerbin"].append(round(vessel.position(ref_frame)[2], 3))
        flight_data["x_start"].append(vessel.position(ref_frame)[0] - x0)
        flight_data["y_start"].append(int(vessel.flight().mean_altitude) - start_mean_altitude)

        if in_loop:
            flight_loop_data["x_kerbin"].append(round(vessel.position(ref_frame)[0], 3))
            flight_loop_data["y_kerbin"].append(round(vessel.position(ref_frame)[2], 3))
            flight_loop_data["x_start"].append(vessel.position(ref_frame)[0] - x0)
            flight_loop_data["y_start"].append(int(vessel.flight().mean_altitude) - start_mean_altitude)


# Функция, записывающая данные во время всего полета и петли в словари с временным интервалом в 1 секунду.
def collect_data_sleep() -> None:
    while not finish:
        time.sleep(0.6)
        speed = int(vessel.flight(ref_frame).speed)

        flight_data["t"].append(vessel.met)
        flight_data["v"].append(speed)
        flight_data["overload"].append(vessel.flight().g_force)
        flight_data["angle"].append(vessel.flight().pitch)
        flight_data["v_x"].append(speed * np.cos(vessel.flight().pitch * np.pi / 180))
        flight_data["v_y"].append(speed * np.sin(vessel.flight().pitch * np.pi / 180))

        if in_loop:
            speed = int(vessel.flight(ref_frame).speed)

            flight_loop_data["t"].append(vessel.met)
            flight_loop_data["v"].append(speed)
            flight_loop_data["overload"].append(vessel.flight().g_force)
            flight_loop_data["angle"].append(vessel.flight().pitch)
            flight_loop_data["v_x"].append(speed * np.cos(vessel.flight().pitch * np.pi / 180))
            flight_loop_data["v_y"].append(speed * np.sin(vessel.flight().pitch * np.pi / 180))


# Функция, записывающая стартовые данные для математической модели.
def collect_start_data() -> None:
    start_speed_x = vessel.flight(ref_frame).horizontal_speed
    start_speed_y = vessel.flight(ref_frame).vertical_speed
    time.sleep(1)
    end_speed_x = vessel.flight(ref_frame).horizontal_speed
    end_speed_y = vessel.flight(ref_frame).vertical_speed

    a_x = end_speed_x - start_speed_x
    a_y = end_speed_y - start_speed_y

    start_data["a_x"] = a_x
    start_data["a_y"] = a_y
    start_data["v_x"] = end_speed_x
    start_data["v_y"] = end_speed_y


# Функция, записывающая все данные из словарей в файлы.
def write_data() -> None:
    write_flight_data()
    write_flight_loop_data()
    write_start_data()


# Функция, записывающая данные всего полета в файл flight_data.json.
def write_flight_data() -> None:
    with open("flight_data.json", "w") as file:
        json.dump(flight_data, file, indent=4)


# Функция, записывающая данные мертвой петли в файл flight_loop_data.json.
def write_flight_loop_data() -> None:
    with open("flight_loop_data.json", "w") as file:
        json.dump(flight_loop_data, file, indent=4)


# Функция, записывающая стартовые данные для математической модели в файл start_data.json.
def write_start_data() -> None:
    with open("start_data.json", "w") as file:
        json.dump(start_data, file, indent=4)


# Функция, отвечающая за стабилизацию курса относительно оси Oy.
def stabilize_heading_to(desired_yaw: float) -> None:
    vessel.control.sas = False
    cur_yaw = round(vessel.flight().heading)
    cur_roll = round(vessel.flight().roll)

    while cur_yaw != desired_yaw:
        if cur_roll < 180:
            if cur_yaw > desired_yaw:
                vessel.control.yaw = -0.25
            elif cur_yaw < desired_yaw:
                vessel.control.yaw = 0.25
        else:
            if cur_yaw > desired_yaw:
                vessel.control.yaw = 0.25
            elif cur_yaw < desired_yaw:
                vessel.control.yaw = -0.25
        cur_yaw = round(vessel.flight().heading)

    vessel.control.sas = True
    vessel.control.yaw = 0


# Функция, отвечающая за стабилизацию курса относительно оси Ox.
def stabilize_roll_to(desired_roll: float) -> None:
    cur_roll = round(vessel.flight().roll)

    while cur_roll != desired_roll:
        if desired_roll == 0:
            if cur_roll > desired_roll:
                vessel.control.roll = -0.1
            elif cur_roll < desired_roll:
                vessel.control.roll = 0.1
        elif desired_roll == 180:
            if cur_roll > 0:
                vessel.control.roll = 0.1
            elif cur_roll < 0:
                vessel.control.roll = -0.1
        cur_roll = round(vessel.flight().roll)

    vessel.control.roll = 0


# Функция, отвечающая за поэтапное выполнение маневра.
def make_loop() -> None:
    start()
    perform_loop()
    turn()
    end()


# Функция, отвечающая за I этап выполнения полета - разгон и взлёт.
def start() -> None:
    vessel.control.throttle = 1.0
    vessel.control.activate_next_stage()

    while True:
        if vessel.flight(ref_frame).horizontal_speed >= target_start_speed:
            break

    current_pitch = vessel.flight().pitch

    while abs(current_pitch - target_pitch_up) > 1:
        if current_pitch < target_pitch_up:
            vessel.control.pitch = 0.1
        elif current_pitch > target_pitch_up:
            vessel.control.pitch = -0.1
        else:
            break
        current_pitch = vessel.flight().pitch

    vessel.control.sas = True
    vessel.control.pitch = 0
    vessel.control.wheels = False

    stabilize_heading_to(90)
    time.sleep(0.5)
    stabilize_roll_to(0)

    while True:
        if vessel.flight().mean_altitude >= target_altitude:
            vessel.control.sas = False
            break

    current_pitch = vessel.flight().pitch

    while abs(current_pitch - horizontal_pitch) > 1:
        if current_pitch < horizontal_pitch:
            vessel.control.pitch = 0.1
        elif current_pitch > horizontal_pitch:
            vessel.control.pitch = -0.1
        else:
            break
        current_pitch = vessel.flight().pitch

    vessel.control.sas = True
    vessel.control.pitch = 0

    stabilize_heading_to(90)

    collect_start_data()

    time.sleep(0.5)
    stabilize_roll_to(0)


# Функция, отвечающая за II этап выполнения полета - манёвр.
def perform_loop() -> None:
    global in_loop
    in_loop = True

    while True:
        if vessel.flight(ref_frame).speed >= target_final_speed:
            start_x_dir = vessel.flight(ref_frame).direction[0]
            break

    while True:
        x_dir = vessel.flight(ref_frame).direction[0]
        vessel.control.pitch = 1
        if x_dir < 0:
            break

    while True:
        x_dir = vessel.flight(ref_frame).direction[0]
        vessel.control.pitch = 1
        if x_dir > 0:
            break

    while True:
        x_dir = vessel.flight(ref_frame).direction[0]
        vessel.control.pitch = 1
        if x_dir >= start_x_dir:
            break

    vessel.control.sas = False
    vessel.control.pitch = 0
    vessel.control.sas = True

    stabilize_heading_to(90)
    time.sleep(0.5)
    stabilize_roll_to(0)


# Функция, отвечающая за III этап выполнения полета - разворот.
def turn() -> None:
    while True:
        if vessel.flight(ref_frame).horizontal_speed >= target_turn_speed:
            break

    global in_loop
    in_loop = False

    rotation_w = vessel.flight(ref_frame).rotation[3]

    time.sleep(0.5)
    if rotation_w > 0:
        while True:
            vessel.control.roll = 0.75
            if vessel.flight(ref_frame).rotation[3] <= 0:
                break
    else:
        while True:
            vessel.control.roll = 0.75
            if vessel.flight(ref_frame).rotation[3] >= 0:
                break

    stabilize_roll_to(180)

    vessel.control.roll = 0
    time.sleep(1)
    vessel.control.sas = False

    while round(vessel.flight(ref_frame).direction[0]) != -1:
        vessel.control.pitch = 0.5

    current_pitch = vessel.flight().pitch

    while abs(current_pitch - horizontal_pitch) > 0.5:
        vessel.control.pitch = 0.5
        current_pitch = vessel.flight().pitch

    vessel.control.pitch = 0
    time.sleep(1)


# Функция, отвечающая за IV этап выполнения полета - посадка.
def end() -> None:
    current_pitch = vessel.flight().pitch
    vessel.control.throttle = 0

    while abs(current_pitch - target_pitch_down) > 0.5:
        if current_pitch > target_pitch_down:
            vessel.control.pitch = -0.1
        elif current_pitch < target_pitch_down:
            vessel.control.pitch = 0.1
        current_pitch = vessel.flight().pitch

    vessel.control.sas = True
    vessel.control.pitch = 0
    stabilize_roll_to(0)

    while True:
        if vessel.flight().mean_altitude <= 170:
            vessel.control.wheels = True
            vessel.control.brakes = True
            vessel.control.lights = True
            break

    while True:
        if vessel.flight().mean_altitude <= 120:
            vessel.control.sas = False
            break

    current_pitch = vessel.flight().pitch

    while current_pitch < horizontal_pitch:
        vessel.control.pitch = 0.1
        current_pitch = vessel.flight().pitch

    vessel.control.sas = True
    vessel.control.pitch = 0

    stabilize_roll_to(0)

    if vessel.flight().speed == 0:
        vessel.control.lights = False

    while True:
        if round(vessel.flight(ref_frame).velocity[0]) == 0:
            vessel.control.sas = False
            vessel.control.lights = False
            break

    global finish
    finish = True


# Точка входа в программу.
def main() -> None:
    with cf.ThreadPoolExecutor() as executor:
        executor.submit(collect_data)
        executor.submit(collect_data_sleep)
        make_loop()
        write_data()


if __name__ == "__main__":
    main()