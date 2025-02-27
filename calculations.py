# Импортируем необходимые библиотеки.
import json
import numpy as np

# Инициализируем словари, в дальнейшем использующийся для получения данных по ключам из других файлов.
flight_loop_data = start_data = {}

# Инициализируем словарь, в дальнейшем использующийся для записи данных математической модели по ключам.
calculations_data = {
    "t": [],  # Время (с).
    "x": [],  # Координата по оси Ox относительно стартовой позиции (взлетной полосы) ЛА (м).
    "y": [],  # Координата по оси Oy относительно стартовой позиции (взлетной полосы) ЛА (м).
    "v": [],  # Общая скорость ЛА (м/с).
    "overload": [],  # Перегрузка (G).
    "angle": [],  # Угол (°).
    "v_x": [],  # Общая скорость ЛА по оси Ox (м/с).
    "v_y": []  # Общая скорость ЛА по оси Oy (м/с).
}

# Инициализируем константные переменные:
t = 0.3  # Шаг времени, с которым будем вычислять параметры во время полета (допустим, что на таком отрезке времени движения равноускоренное).
overload = 1  # Начальное значение перегрузки (в G).
g = 9.81  # Ускорение свободного падения (в м/с²). Значение константно, т.к. миссия проходит без выхода в космическое пространство.
Ft = 85_000  # Максимальная сила тяги двигателя ЛА (в Н). Значение взято из KSP.
m = 6985  # Масса ЛА (в кг). Значение взято из KSP константно, поскольку изменение массы за счёт сгорания топлива ничтожно мало.
S_WING = 20.09  # Площадь крыла ЛА (в м²). Значение высчитано в программе 3ds Max.
S_FRONT = 4.67  # Площадь проекции ЛА на плоскость, перпендикулярную направлению движения ЛА (в м²). Значение высчитано в программе 3ds Max.
RHO_0 = 1.225  # Плотность воздуха на уровне моря, значение константно.
H = 5600  # Характеристическая высота (в м). Значение взято с сайта wiki.kerbalspaceprogram.com для планеты Kerbin.
Fg = g * m  # Сила притяжения на планете Kerbin (в Н). Значение константно, т.к. миссия проходит без выхода в космическое пространство.
kerbin_radius = 600_000  # Радиус планеты Kerbin (в м). Значение взято с сайта wiki.kerbalspaceprogram.com.
T = 40  # Время начала выполнения маневра относительно начала полета (в с). Параметр используется для построения графиков.
LOOP_RADIUS = 600  # Радиус "мертвой" петли (в м). Значение получено из полета в KSP.

# Инициализируем переменные:
x = y = v_x = v_y = a_x = a_y = h = c_x = c_y = v = air_density = drag = lift = Fc = 0


# Функция, загружающая данные из других файлов.
def load_data() -> None:
    load_flight_loop_data()
    load_start_data()


# Функция, загружающая данные мертвой петли из другого файла.
def load_flight_loop_data() -> None:
    global flight_loop_data
    with open("flight_loop_data.json", "r") as file:
        flight_loop_data = json.load(file)


# Функция, загружающая стартовые данные для математической модели из другого файла.
def load_start_data() -> None:
    global start_data
    with open("start_data.json", "r") as file:
        start_data = json.load(file)


# Функция, инициализирующая переменные из других файлов.
def initialize_variables_from_data() -> None:
    global x, y, v_x, v_y, a_x, a_y

    x = flight_loop_data["x_start"][0]
    y = flight_loop_data["y_start"][0]
    v_x = start_data["v_x"]
    v_y = start_data["v_y"]
    a_x = start_data["a_x"]
    a_y = start_data["a_y"]


# Функция, инициализирующая переменные стартовыми значениями.
def initialize_start_variables() -> None:
    global h, c_x, c_y, v, air_density, drag, lift

    h = np.sqrt(x ** 2 + y ** 2)  # Высота полета ЛА над уровнем моря (в м).
    c_x = 0.3 if abs(
            angle_while_acceleration() * np.pi / 180) > 20 else 0.05  # Коэффициент аэродинамического сопротивления в зависимости от угла атаки ЛА. Оба значения были получены из KSP опытным путем.
    c_y = 5.2 if abs(
            angle_while_acceleration() * np.pi / 180) > 20 else 0.6  # Коэффициент подъемной силы крыла в зависимости от угла атаки ЛА. Оба значения были получены из KSP опытным путем.
    v = np.sqrt(v_x ** 2 + v_y ** 2)  # Общая скорость ЛА
    air_density = RHO_0 * np.exp(-h / H)  # Плотность воздуха относительно высоты (в м).
    drag = 0.5 * air_density * (v ** 2) * c_x * S_FRONT  # Сила аэродинамического сопротивления ЛА (в Н).
    lift = 0.5 * air_density * (v ** 2) * c_y * S_WING  # Подъемная сила крыла ЛА (в Н).


# Функция, возвращающая угол во время набора скорости перед совершением "мертвой" петли.
def angle_while_acceleration() -> int:
    return 0


# Функция, возвращающая угол во время 1-го этапа выполнения "мертвой" петли.
def angle_while_loop_I() -> float:
    return 90 * (T - 41.5) / 5


# Функция, возвращающая угол во время 2-го этапа выполнения "мертвой" петли.
def angle_while_loop_II() -> float:
    return 90 + 90 * (T - 46.5) / 5


# Функция, возвращающая угол во время 3-го этапа выполнения "мертвой" петли.
def angle_while_loop_III() -> float:
    return 180 + 90 * (T - 51.5) / 5


# Функция, возвращающая угол во время 4-го этапа выполнения "мертвой" петли.
def angle_while_loop_IV() -> float:
    return 270 + 90 * (T - 56.5) / 5


# Функция, возвращающая угол во время набора скорости перед разворотом для посадки.
def angle_after_loop() -> int:
    return 0


# Функция, считающая необходимые для математической модели параметры в зависимости от этапа выполнения манёвра.
def calculate(alpha: float, flag: int) -> None:
    global t, drag, lift, a_x, a_y, v, v_x, v_y, x, y, h, T, c_x, c_y, air_density, overload, Fc
    a = flag * (
            a_x ** 2 + a_y ** 2) ** 0.5  # Общее ускорение ЛА (в м/с²). Параметр flag помогает избавиться от модуля на 1-2 этапах выполнения петли.
    T += 0.3  # Добавляем шаг расчетов к общему времени выполнения миссии.
    v_x += a_x * t  # Общая скорость ЛА по оси Ox (м/с).
    v_y += a_y * t  # Общая скорость ЛА по оси Oy (м/с).
    x += v_x * t + (a_x * t ** 2) / 2  # Координата по оси Ox ЛА (в м).
    y += v_y * t + (a_y * t ** 2) / 2  # Координата по оси Oy ЛА (в м).
    h = np.sqrt(x ** 2 + y ** 2)  # Считаем высоту полета ЛА над уровнем моря.
    v = np.sqrt(v_x ** 2 + v_y ** 2)  # Считаем общую скорость ЛА.
    c_x = 0.3 if abs(alpha) > 20 else 0.05  # Возвращаем необходимый коэффициент аэродинамического сопротивления ЛА.
    c_y = 5.2 if abs(alpha) > 20 else 0.6  # Возвращаем необходимый коэффициент подъемной силы крыла ЛА.
    a_x = ((Ft - drag - lift) * np.cos(alpha * np.pi / 180)) / m  # Общее ускорение ЛА по оси Ox (м/с²).
    a_y = ((Ft - drag + lift) * np.sin(alpha * np.pi / 180) - Fg) / m  # Общее ускорение ЛА по оси Oy (м/с²).

    air_density = RHO_0 * np.exp(-h / H)  # Считаем плотность воздуха вокруг борта ЛА в данный момент времени.
    drag = 0.5 * air_density * (
            v ** 2) * c_x * S_FRONT  # Считаем величину силы аэродинамического сопротивления ЛА в данный момент времени.
    lift = 0.5 * air_density * (
            v ** 2) * c_y * S_WING  # Считаем величину подъемной силы крыла ЛА в данный момент времени.

    overload = a / g  # Считаем перегрузку

    collect_data(alpha)


# Функция, считающая необходимые для математической модели параметры.
def start_calculations() -> None:
    while v < 250:
        calculate(angle_while_acceleration(), 1)
    while h <= 1670:
        calculate(angle_while_loop_I(), -1)
    while h <= 2270:
        calculate(angle_while_loop_II(), -1)
    while h >= 1670:
        calculate(angle_while_loop_III(), 1)
    while h > 1070:
        calculate(angle_while_loop_IV(), 1)
    while v < 195:
        calculate(angle_after_loop(), 1)


# Функция, записывающая данные математической модели.
def collect_data(alpha: float) -> None:
    calculations_data["t"].append(T)
    calculations_data["x"].append(x)
    calculations_data["y"].append(y)
    calculations_data["v"].append(v)
    calculations_data["overload"].append(overload)
    calculations_data["angle"].append(alpha)
    calculations_data["v_x"].append(v_x)
    calculations_data["v_y"].append(v_y)


# Функция, записывающая данные атематической модели в файл calculations_data.json.
def write_data() -> None:
    with open("calculations_data.json", "w") as file:
        json.dump(calculations_data, file, indent=4)


# Точка входа в программу.
def main() -> None:
    load_data()
    initialize_variables_from_data()
    initialize_start_variables()
    start_calculations()
    write_data()


if __name__ == "__main__":
    main()
