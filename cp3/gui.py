import taichi as ti
import taichi.math as tm
import time


@ti.data_oriented
class BaseShader:
    """
    Базовый класс шейдера: хранит буфер пикселей, считает цвет каждого
    пикселя через метод main_image и выводит кадры в окно taichi.
    """

    def __init__(self,
                 title: str,
                 res: tuple[int, int] | None = None,
                 gamma: float = 2.2
                 ):
        """
        Создает буфер пикселей и сохраняет параметры окна.

        :param title: заголовок окна
        :param res: разрешение окна (ширина, высота) в пикселях
        :param gamma: гамма коррекция (если <= 0, то не применяется)
        """
        self.title = title
        self.res = res if res is not None else (1000, 563)
        self.resf = tm.vec2(*self.res)
        self.pixels = ti.Vector.field(3, dtype=ti.f32, shape=self.res)
        self.gamma = gamma

    @ti.kernel
    def init(self):
        """
        Начальная инициализация данных (вызывается один раз перед основным циклом).
        В базовом классе ничего не делает (метод рассчитан под перегрузку в наследнике).
        """
        pass

    @ti.kernel
    def calculate(self, t: ti.f32, cursor: tm.vec2):
        """
        Дополнительные вычисления перед отрисовкой кадра.
        В базовом классе также ничего не делает.

        :param t: время, прошедшее от первого кадра, с
        :param cursor: положение курсора мыши (от 0 до 1 по каждой оси)
        """
        pass

    @ti.func
    def main_image(self, uv, t, cursor):
        """
        Вычисляет цвет одного пикселя. Этот метод перегружается в наследниках.

        :param uv: координаты пикселя (центр экрана - (0, 0), высота экрана равна 1)
        :param t: время, прошедшее от первого кадра, с
        :param cursor: положение курсора мыши
        :return: цвет пикселя tm.vec3 (RGB, линейное пространство)
        """
        col = tm.vec3(0.)
        col.rg = uv + 0.5
        return col

    @ti.kernel
    def render(self, t: ti.f32, cursor: tm.vec2):
        """
        Расчет цветов всех пикселей кадра (внешний цикл распараллеливается).

        :param t: время, прошедшее от первого кадра, с
        :param cursor: положение курсора мыши
        """
        for fragCoord in ti.grouped(self.pixels):
            uv = (fragCoord - 0.5 * self.resf) / self.resf.y
            col = self.main_image(uv, t, cursor)
            if self.gamma > 0:
                col = tm.clamp(col ** (1 / self.gamma), 0., 1.)
            self.pixels[fragCoord] = col

    def main_loop(self):
        """
        Основной цикл: создает окно, на каждой итерации пересчитывает время,
        отрисовывает кадр и выводит его на экран.
        """
        gui = ti.GUI(self.title, res=self.res, fast_gui=True)
        start = time.time()

        self.init()
        while gui.running:  # основной цикл
            if gui.get_event(ti.GUI.PRESS):  # для закрытия приложения по нажатию на Esc
                if gui.event.key == ti.GUI.ESCAPE:
                    break

            t = time.time() - start  # пересчет времени, прошедшего с первого кадра
            cursor = gui.get_cursor_pos()
            self.calculate(t, cursor)
            self.render(t, cursor)  # расчет цветов пикселей
            gui.set_image(self.pixels)  # перенос пикселей из поля pixels в буфер кадра
            gui.show()

        gui.close()


if __name__ == "__main__":
    ti.init(arch=ti.opengl)

    shader = BaseShader("Base shader")

    shader.main_loop()
