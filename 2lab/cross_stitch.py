import json
import os
from PIL import Image, ImageDraw
import numpy as np
from sklearn.cluster import KMeans

def load_dmc_colors():
    with open('dmc_colors.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def find_nearest_dmc_color(rgb_color, dmc_colors):
    min_distance = float('inf')
    nearest_color = None
    for dmc_color in dmc_colors:
        dmc_rgb = np.array(dmc_color['rgb'])
        distance = np.linalg.norm(dmc_rgb - rgb_color)
        if distance < min_distance:
            min_distance = distance
            nearest_color = dmc_color
    return nearest_color

def convert_image_to_cross_stitch(image_path, max_colors=20, max_stitches=100):
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    width, height = image.size
    aspect_ratio = width / height
    
    if width > height:
        new_width = max_stitches
        new_height = int(max_stitches / aspect_ratio)
    else:
        new_height = max_stitches
        new_width = int(max_stitches * aspect_ratio)
    
    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    colors = []
    for y in range(new_height):
        for x in range(new_width):
            colors.append(image.getpixel((x, y)))
    
    colors = np.array(colors)
    
    if len(colors) > max_colors:
        kmeans = KMeans(n_clusters=max_colors, random_state=42, n_init=10)
        labels = kmeans.fit_predict(colors)
        cluster_centers = kmeans.cluster_centers_
    else:
        labels = list(range(len(colors)))
        cluster_centers = colors
    
    dmc_colors = load_dmc_colors()
    dmc_palette = [find_nearest_dmc_color(center, dmc_colors) for center in cluster_centers]
    
    stitch_size = 20
    schema_width = new_width * stitch_size
    schema_height = new_height * stitch_size
    schema = Image.new('RGB', (schema_width, schema_height), 'white')
    draw = ImageDraw.Draw(schema)
    
    symbols = ['@', '#', '$', '%', '&', '*', '+', '-', '=', '?', 
               '/', '>', '<', '!', '^', '~', '|', '(', ')', '[', ']',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
               'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    for y in range(new_height):
        for x in range(new_width):
            color_index = labels[y * new_width + x]
            dmc_color = dmc_palette[color_index]
            symbol = symbols[color_index % len(symbols)]
            
            top_left = (x * stitch_size, y * stitch_size)
            bottom_right = ((x + 1) * stitch_size, (y + 1) * stitch_size)
            
            draw.rectangle([top_left, bottom_right], 
                         fill=tuple(dmc_color['rgb']), 
                         outline='black', width=1)
            
            text_x = top_left[0] + stitch_size // 4
            text_y = top_left[1] + stitch_size // 4
            draw.text((text_x, text_y), symbol, fill='black')
    
    for i in range(0, schema_width, stitch_size * 10):
        draw.line([(i, 0), (i, schema_height)], fill='black', width=2)
    for i in range(0, schema_height, stitch_size * 10):
        draw.line([(0, i), (schema_width, i)], fill='black', width=2)
    
    legend_width = 300
    legend_height = len(dmc_palette) * 25 + 50
    legend = Image.new('RGB', (legend_width, legend_height), 'white')
    draw_legend = ImageDraw.Draw(legend)
    
    draw_legend.text((10, 10), "ЛЕГЕНДА", fill='black')
    
    for i, dmc_color in enumerate(dmc_palette):
        symbol = symbols[i % len(symbols)]
        y_pos = 40 + i * 25
        
        color_box = (10, y_pos, 30, y_pos + 20)
        draw_legend.rectangle(color_box, fill=tuple(dmc_color['rgb']), outline='black')
        
        text = f"{symbol} - DMC {dmc_color['dmc']}"
        draw_legend.text((40, y_pos + 5), text, fill='black')
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    schema.save(f"{base_name}_schema.png")
    legend.save(f"{base_name}_legend.png")
    
    print(f"Схема сохранена: {base_name}_schema.png")
    print(f"Легенда сохранена: {base_name}_legend.png")
    print(f"Использовано цветов: {len(dmc_palette)}")
    print(f"Размер схемы: {new_width}x{new_height} крестиков")

def get_user_input():
    print("=== Конвертер изображений в схемы вышивки крестиком ===\n")
    
    while True:
        image_path = input("Введите название изображения (например: photo.jpg): ").strip()
        if not image_path:
            print("Ошибка: Путь к изображению не может быть пустым!")
            continue
        if not os.path.exists(image_path):
            print(f"Ошибка: Файл '{image_path}' не найден!")
            print("Убедитесь, что файл существует и путь указан правильно.")
            continue
        break
    
    while True:
        try:
            colors_input = input("Введите количество цветов ниток (по умолчанию 20): ").strip()
            if not colors_input:
                max_colors = 20
                break
            max_colors = int(colors_input)
            if max_colors < 1 or max_colors > 50:
                print("Ошибка: Количество цветов должно быть от 1 до 50!")
                continue
            break
        except ValueError:
            print("Ошибка: Введите число!")
    
    while True:
        try:
            stitches_input = input("Введите максимальный размер схемы в крестиках (по умолчанию 100): ").strip()
            if not stitches_input:
                max_stitches = 100
                break
            max_stitches = int(stitches_input)
            if max_stitches < 10 or max_stitches > 500:
                print("Ошибка: Размер схемы должен быть от 10 до 500 крестиков!")
                continue
            break
        except ValueError:
            print("Ошибка: Введите число!")
    
    return image_path, max_colors, max_stitches

if __name__ == "__main__":
    image_path, max_colors, max_stitches = get_user_input()
    
    print(f"\nНачинаем конвертацию...")
    print(f"Изображение: {image_path}")
    print(f"Количество цветов: {max_colors}")
    print(f"Размер схемы: {max_stitches} крестиков")
    print()
    
    convert_image_to_cross_stitch(image_path, max_colors, max_stitches)