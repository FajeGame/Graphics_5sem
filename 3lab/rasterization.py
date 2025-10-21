import matplotlib.pyplot as plt
import numpy as np

# Настройки сетки
GRID_SIZE_MM = 2.5  # Размер ячейки в миллиметрах
DPI = 100  # Разрешение для расчета (dots per inch)

def create_grid(width_mm=80, height_mm=60):
    """
    Создает квадратную сетку с заданным размером ячейки.
    
    width_mm, height_mm - размеры канвы в миллиметрах
    """
    # Преобразуем размеры в пиксели
    width_px = int(width_mm * DPI / 25.4)
    height_px = int(height_mm * DPI / 25.4)
    cell_size_px = int(GRID_SIZE_MM * DPI / 25.4)
    
    # Создаем фигуру
    fig, ax = plt.subplots(figsize=(width_mm/25.4, height_mm/25.4), dpi=DPI)
    
    # Рисуем вертикальные линии
    for x in range(0, width_px, cell_size_px):
        ax.axvline(x, color='lightgray', linewidth=0.5)
    
    # Рисуем горизонтальные линии
    for y in range(0, height_px, cell_size_px):
        ax.axhline(y, color='lightgray', linewidth=0.5)
    
    ax.set_xlim(0, width_px)
    ax.set_ylim(0, height_px)
    ax.set_aspect('equal')
    ax.invert_yaxis()  # Инвертируем ось Y для удобства
    
    return fig, ax, cell_size_px, width_px, height_px


def bresenham_line(x0, y0, x1, y1):
    """
    Алгоритм Брезенхема для растеризации отрезка.
    
    Возвращает список точек (x, y), которые должны быть закрашены.
    """
    points = []
    
    # Переходим к целым координатам
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    
    # Если отрезок вертикальный
    if x0 == x1:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            points.append((x0, y))
        return points
    
    # Вычисляем шаги и изменения
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    
    # Определяем направление градиента
    steep = dy > dx
    
    # Если градиент крутой, меняем x и y местами
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
        dx, dy = dy, dx
    
    # Определяем направление движения по X
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
    
    # Параметры алгоритма
    error = 0
    delta_error = dy
    y = y0
    y_step = 1 if y1 > y0 else -1
    
    # Рисуем отрезок
    for x in range(x0, x1 + 1):
        if steep:
            points.append((y, x))  # Меняем обратно, если поменяли местами
        else:
            points.append((x, y))
        
        error += delta_error
        if 2 * error >= dx:
            y += y_step
            error -= dx
    
    return points


def bresenham_circle(center_x, center_y, radius):
    """
    Алгоритм Брезенхема для растеризации окружности.
    
    Рисует окружность, используя симметрию относительно осей.
    """
    points = []
    x = 0
    y = radius
    d = 3 - 2 * radius  # Параметр принятия решения
    
    # Функция для добавления симметричных точек
    def add_circle_points(cx, cy, x, y):
        points.extend([
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x),
            (cx + y, cy - x), (cx - y, cy - x)
        ])
    
    # Первая точка
    add_circle_points(center_x, center_y, x, y)
    
    # Рисуем окружность пока x <= y
    while x <= y:
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y -= 1
        x += 1
        add_circle_points(center_x, center_y, x, y)
    
    return points


def draw_rasterized_points(ax, points, color='red', marker='s', size=100):
    """
    Рисует точки на сетке.
    
    points - список координат (x, y)
    """
    if not points:
        return
    
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    
    ax.scatter(x_coords, y_coords, c=color, marker=marker, s=size, 
               edgecolors='black', linewidths=0.5, zorder=5)


def main():
    """
    Основная функция программы.
    """
    # Создаем сетку
    fig, ax, cell_size, width, height = create_grid()
    
    # Пример 1: Растеризация отрезка
    print("Растеризация отрезка от (10, 10) до (80, 50)")
    line_points = bresenham_line(10, 10, 80, 50)
    draw_rasterized_points(ax, line_points, color='blue', marker='s')
    
    # Пример 2: Растеризация окружности
    print("Растеризация окружности с центром (40, 30) и радиусом 20")
    circle_points = bresenham_circle(40, 30, 20)
    draw_rasterized_points(ax, circle_points, color='red', marker='s')
    
    ax.set_title('Растеризация отрезка и окружности', fontsize=14, pad=20)
    ax.set_xlabel('X', fontsize=12)
    ax.set_ylabel('Y', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('rasterization_result.png', dpi=DPI, bbox_inches='tight')
    print("Результат сохранен в файл 'rasterization_result.png'")
    plt.show()


if __name__ == "__main__":
    main()

