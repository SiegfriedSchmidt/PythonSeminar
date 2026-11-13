"""
Горлачев Матвей БПМ 241
Вариант 9

Декомпозиция

---
1. Элементы анимации
1.1 Черный фон

1.2 Квадраты со скругленными углами (только их границы) задаются SDF скругленного квадрата
    https://iquilezles.org/articles/distfunctions2d/ , Rounded Box

1.3 Поток квадратов. Каждые 0.1 с появляется новый квадрат, каждый следующий немного
    больше предыдущего. Через 20 квадратов (2 секунды на один цикл из 20 квадратов) размеры начинаются заново.
    Каждый квадрат живет примерно 1.3 с, поэтому старые исчезают, пока появляются новые.
    Пока квадрат жив, он вращается по часовой стрелке, и чем он больше, тем быстрее

1.4 Неоновое свечение, яркость спадает как 1 / d^2 от контура, тонкое яркое ядро и широкий ореол.
    Свечения всех квадратов складываются, на пересечениях линии белеют

1.5 Цвет, косинусная палитра по номеру квадрата в цикле (3 круга палитры за цикл)

---
2. Функции (f(x) и f(x, t)) и ссылки на graphtoy
2.1. Полуразмер квадрата: size(j) = 0.1 + 0.3 * sqrt(j / 20), (j это номер квадрата в цикле)
    https://graphtoy.com/?f1(x,t)=0.1%2B0.3%2Asqrt%28x%2F20%29&v1=true&f2(x,t)=&v2=false&f3(x,t)=&v3=false&f4(x,t)=&v4=false&f5(x,t)=&v5=false&f6(x,t)=&v6=false&grid=1&coords=10,0.3,12

2.2. Появление / исчезновение (x = возраст квадрата в секундах):
    alpha(x) = smoothstep(0, 0.05, x) * (1 - smoothstep(1.2, 1.3, x))
    https://graphtoy.com/?f1(x,t)=smoothstep%280%2C0.05%2Cx%29%2A%281-smoothstep%281.2%2C1.3%2Cx%29%29&v1=true&f2(x,t)=&v2=false&f3(x,t)=&v3=false&f4(x,t)=&v4=false&f5(x,t)=&v5=false&f6(x,t)=&v6=false&grid=1&coords=0.7,0.5,1

2.3. Угол поворота: angle(j, t) = -4 * sin(0.1 * j) + 0.03 * (j + 1) * t
    - начальный угол - синус от номера (x = j):
    https://graphtoy.com/?f1(x,t)=-4%2Asin%280.1%2Ax%29&v1=true&f2(x,t)=&v2=false&f3(x,t)=&v3=false&f4(x,t)=&v4=false&f5(x,t)=&v5=false&f6(x,t)=&v6=false&grid=1&coords=10,-2,12
    - скорость 0.03 * (j + 1) рад/с: большие квадраты крутятся быстрее.
    Угол от времени для j = 0, 10, 19 (x = t):
    https://graphtoy.com/?f1(x,t)=-4%2Asin%280.1%2A0%29%2B0.03%2A%280%2B1%29%2Ax&v1=true&f2(x,t)=-4%2Asin%280.1%2A10%29%2B0.03%2A%2810%2B1%29%2Ax&v2=true&f3(x,t)=-4%2Asin%280.1%2A19%29%2B0.03%2A%2819%2B1%29%2Ax&v3=true&f4(x,t)=&v4=false&f5(x,t)=&v5=false&f6(x,t)=&v6=false&grid=1&coords=5,0,8

2.4. Свечение (x = d - расстояние до контура): glow(d) = (0.008 / (abs(d) + 0.004))^2
    и после тональной компрессии 1 - exp(-glow):
    https://graphtoy.com/?f1(x,t)=pow%280.008%2F%28abs%28x%29%2B0.004%29%2C2%29&v1=true&f2(x,t)=1-exp%28-pow%280.008%2F%28abs%28x%29%2B0.004%29%2C2%29%29&v2=true&f3(x,t)=&v3=false&f4(x,t)=&v4=false&f5(x,t)=&v5=false&f6(x,t)=&v6=false&grid=1&coords=0,1,0.1

2.5. Палитра (https://iquilezles.org/articles/palettes/):
    pal(x) = 0.6 + 0.5 * cos(2 * pi * (x + (0.1, 0.3, 0.5))),  x = 3 * j / 20
    R, G, B каналы - одна и та же косинусоида со сдвигом фазы на 0.2:
    https://graphtoy.com/?f1(x,t)=0.6%2B0.5%2Acos%282%2API%2A%28x%2B0.1%29%29&v1=true&f2(x,t)=0.6%2B0.5%2Acos%282%2API%2A%28x%2B0.3%29%29&v2=true&f3(x,t)=0.6%2B0.5%2Acos%282%2API%2A%28x%2B0.5%29%29&v3=true&f4(x,t)=&v4=false&f5(x,t)=&v5=false&f6(x,t)=&v6=false&grid=1&coords=0.5,0.5,1

---
3. Взаимосвязи
- время t -> номер последнего появившегося квадрата n_last = floor(t / 0.1)
- перебираем последние 14 квадратов n = n_last, n_last - 1, ...
- n -> возраст (t - 0.1 * n) -> alpha (2.2)
- n -> j -> размер (2.1), цвет (2.5); j и t -> угол (2.3)
- угол -> поворот координат пикселя; размер -> SDF (1.2) -> свечение (2.4)
- сумма свечений * цвет * alpha -> компрессия 1 - exp(-x) -> гамма-коррекция (в BaseShader) -> цвет пикселя

---
4. Реализация
- класс StreamShader наследуется от BaseShader (gui.py) и перегружает main_image
- функции ti.func: rot, sd_round_box, rect_size, rect_angle, rect_alpha, palette, glow.
"""
import taichi as ti
import taichi.math as tm

from gui import BaseShader

# Квадраты
DT = 0.1  # промежуток между появлениями квадратов
N_CYCLE = 20  # квадратов в одном цикле
LIFE = 1.3  # время жизни квадрата
MAX_VISIBLE = 14  # у скольких последних квадратов проверять время жизни

# Косинусная палитра https://iquilezles.org/articles/palettes/
PAL_D = tm.vec3(0.1, 0.3, 0.5)  # сдвиги фаз каналов R, G, B


@ti.func
def rot(a):
    """
    Матрица поворота на угол a.

    :param a: угол, рад
    :return: матрица 2x2
    """
    c = ti.cos(a)
    s = ti.sin(a)
    return tm.mat2([c, -s], [s, c])


@ti.func
def sd_round_box(p, b, r):
    """
    SDF квадрата со скругленными углами (центр в начале координат).

    :param p: точка tm.vec2
    :param b: полуразмер квадрата
    :param r: радиус скругления углов
    :return: расстояние до границы
    """
    q = ti.abs(p) - (b - r)
    return ti.max(q, 0.0).norm() + ti.min(ti.max(q.x, q.y), 0.0) - r


@ti.func
def rect_size(j):
    """
    Полуразмер квадрата по его номеру внутри цикла.

    :param j: номер квадрата в цикле (0 .. N_CYCLE - 1)
    :return: полуразмер
    """
    return 0.1 + 0.3 * ti.sqrt(j / N_CYCLE)


@ti.func
def rect_angle(j, t):
    """
    Угол поворота квадрата: начальный угол - синус от номера в цикле,
    дальше квадрат вращается по часовой стрелке, причем чем больше
    номер, тем быстрее.

    :param j: номер квадрата в цикле
    :param t: время, с
    :return: угол, рад
    """
    start = -4.0 * ti.sin(0.1 * j)  # начальный угол
    speed = 0.03 * (j + 1)  # скорость вращения, рад/с
    return start + speed * t


@ti.func
def rect_alpha(age):
    """
    Прозрачность квадрата: плавно появляется и плавно исчезает.

    :param age: возраст квадрата, с
    :return: множитель яркости от 0 до 1
    """
    fade_in = tm.smoothstep(0.0, 0.05, age)
    fade_out = 1.0 - tm.smoothstep(LIFE - 0.1, LIFE, age)
    return fade_in * fade_out


@ti.func
def palette(x):
    """
    Косинусная палитра.
    Возводим в квадрат, чтобы перейти в линейное пространство (гамма коррекция есть в BaseShader).

    :param x: параметр палитры
    :return: цвет tm.vec3
    """
    col = 0.6 + 0.5 * ti.cos(2.0 * tm.pi * (x + PAL_D))
    return col * col


@ti.func
def glow(d):
    """
    Неоновое свечение линии: яркость спадает как 1 / abs(d)^2.
    тонкое яркое ядро и широкий цветной ореол.

    :param d: расстояние со знаком до линии
    :return: яркость
    """
    k = 0.008 / (ti.abs(d) + 0.004)
    return k * k


@ti.data_oriented
class StreamShader(BaseShader):
    """
    Шейдер наследованный от BaseShader
    """

    @ti.func
    def main_image(self, uv, t, cursor):
        """
        Цвет пикселя: сумма свечений всех видимых квадратов.

        :param uv: координаты пикселя (центр экрана - (0, 0), высота экрана равна 1)
        :param t: время, с
        :param cursor: положение курсора (здесь мы его не используем)
        :return: цвет пикселя tm.vec3
        """
        col = tm.vec3(0.0)
        n_last = ti.floor(t / DT)  # номер последнего появившегося квадрата
        for k in ti.static(range(MAX_VISIBLE)):
            n = n_last - k
            age = t - n * DT
            if age < LIFE:
                c = ti.floor(n / N_CYCLE)  # номер цикла
                j = n - c * N_CYCLE  # номер в цикле
                b = rect_size(j)
                p = rot(rect_angle(j, t)) @ uv
                d = sd_round_box(p, b, 0.4 * b)  # скругление углов - 40% полуразмера
                color = palette(3.0 * j / N_CYCLE)  # 3 круга палитры за цикл
                col += color * glow(d) * rect_alpha(age)
        # tone mapping
        return 1.0 - ti.exp(-col)


if __name__ == "__main__":
    ti.init(arch=ti.gpu)
    shader = StreamShader("Variant 9", res=(1000, 563))
    shader.main_loop()
