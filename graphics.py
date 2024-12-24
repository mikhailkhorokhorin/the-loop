# Импортируем необходимые библиотеки.
import json
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# Инициализируем словари, в дальнейшем использующийся для получения данных по ключам из других файлов.
flight_data = flight_loop_data = calculations_data = {}


# Функция, загружающая данные из других файлов.
def load_data() -> None:
    load_flight_data()
    load_flight_loop_data()
    load_calculations_data()


# Функция, загружающая данные всего полета из другого файла.
def load_flight_data() -> None:
    global flight_data
    with open("flight_data.json", "r") as file:
        flight_data = json.load(file)


# Функция, загружающая данные мертвой петли из другого файла.
def load_flight_loop_data() -> None:
    global flight_loop_data
    with open("flight_loop_data.json", "r") as file:
        flight_loop_data = json.load(file)


# Функция, загружающая данные математической модели из другого файла.
def load_calculations_data() -> None:
    global calculations_data
    with open("calculations_data.json", "r") as file:
        calculations_data = json.load(file)


# Функция, выводящая на экран сравнение графиков траектории мертвой петли математической модели и данных полета.
def show_flight_loop_graphic() -> None:
    plt.subplot(1, 1, 1)
    plt.plot(flight_loop_data["x_start"], flight_loop_data["y_start"], label="KSP")
    plt.plot(calculations_data["x"], calculations_data["y"], label="MAT")
    plt.title("OXY")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend(fontsize=9)
    plt.show()


# Функция, выводящая на экран сравнение графиков траектории всего полета математической модели и данных полета.
def show_flight_graphic() -> None:
    plt.subplot(1, 1, 1)
    plt.plot(flight_data["x_start"], flight_data["y_start"], label="KSP")
    plt.plot(calculations_data["x"], calculations_data["y"], label="MAT")
    plt.title("OXY")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend(fontsize=9)
    plt.show()


# Функция, выводящая на экран сравнение графиков зависимости угла от времени математической модели и данных полета.
def show_angle_graphic() -> None:
    calculations_data_t = np.linspace(min(calculations_data["t"]), max(calculations_data["t"]), 20)
    spl = make_interp_spline(calculations_data["t"], calculations_data["angle"], k=1)
    calculations_data_angle = spl(calculations_data_t)
    plt.subplot(1, 1, 1)
    plt.plot(calculations_data_t, calculations_data_angle, label="MAT")
    plt.plot(flight_loop_data["t"], flight_loop_data["angle"], label="KSP")
    plt.title("График зависимости угла от времени")
    plt.xlabel("Время, с")
    plt.ylabel("Угол, °")
    plt.legend(fontsize=9)
    plt.show()


# Функция, выводящая на экран сравнение графиков зависимости скорости от времени математической модели и данных полета.
def show_speed_graphic() -> None:
    calculations_data_t = np.linspace(min(calculations_data["t"]), max(calculations_data["t"]), 300)
    spl = make_interp_spline(calculations_data["t"], calculations_data["v"])
    calculations_data_v = spl(calculations_data_t)

    plt.subplot(1, 1, 1)
    plt.plot(calculations_data_t, calculations_data_v, label="MAT")
    plt.plot(flight_loop_data["t"], flight_loop_data["v"], label="KSP")
    plt.title("График зависимости скорости от времени")
    plt.xlabel("Время, с")
    plt.ylabel("Скорость, м/с")
    plt.legend(fontsize=9)
    plt.show()


# Функция, выводящая на экран сравнение графиков зависимости перегрузки от времени математической модели и данных полета.
def show_overload_graphic() -> None:
    calculations_data_t = np.linspace(min(calculations_data["t"]), max(calculations_data["t"]), 50)
    spl = make_interp_spline(calculations_data["t"], calculations_data["overload"])
    calculations_data_overload = spl(calculations_data_t)

    plt.subplot(1, 1, 1)
    plt.plot(calculations_data_t, calculations_data_overload, label="MAT")
    plt.plot(flight_loop_data["t"], flight_loop_data["overload"], label="KSP")
    plt.title("График зависимости перегрузки от времени")
    plt.xlabel("Время, с")
    plt.ylabel("Перегрузка, G")
    plt.legend(fontsize=9)
    plt.show()


# Точка входа в программу.
def main() -> None:
    load_data()
    show_flight_loop_graphic()
    show_flight_graphic()
    show_angle_graphic()
    show_speed_graphic()
    show_overload_graphic()


if __name__ == "__main__":
    main()

