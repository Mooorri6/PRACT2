#!/usr/bin/env python3
"""
Анализатор PIV логов - простой вариант
Только 2 графика: 
1. Долгота от времени
2. Траектория (широта vs долгота)
"""

import re
import matplotlib.pyplot as plt

def parse_piv_log(filename):
    """Парсим лог и извлекаем время, широту и долготу"""
    print(f"Чтение файла: {filename}")
    
    times = []
    latitudes = []
    longitudes = []
    
    # Паттерны для поиска координат в разных типах сообщений
    patterns = [
        r'(\d+\.\d+) PIV_ID INERTIAL LAT\s+(-?\d+\.\d+) deg LON\s+(-?\d+\.\d+)',
        r'(\d+\.\d+) PIV_ID COMP.*?LAT\s+(-?\d+\.\d+) deg LON\s+(-?\d+\.\d+)',
        r'(\d+\.\d+) PIV_ID GNSS.*?lat\s+(-?\d+\.\d+) lon\s+(-?\d+\.\d+)'
    ]
    
    with open(filename, 'r') as f:
        for line in f:
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    time = float(match.group(1))
                    lat = float(match.group(2))
                    lon = float(match.group(3))
                    
                    times.append(time)
                    latitudes.append(lat)
                    longitudes.append(lon)
                    break  # Нашли - переходим к следующей строке
    
    print(f"Найдено точек: {len(times)}")
    if times:
        print(f"Первая точка: время={times[0]:.2f}с, lat={latitudes[0]:.6f}, lon={longitudes[0]:.6f}")
        print(f"Последняя точка: время={times[-1]:.2f}с, lat={latitudes[-1]:.6f}, lon={longitudes[-1]:.6f}")
    
    return times, latitudes, longitudes

def plot_simple_graphs(times, latitudes, longitudes, filename):
    """Строим два графика как в задании"""
    
    # Создаем фигуру с двумя графиками рядом
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. ГРАФИК: Долгота от времени
    ax1.plot(times, longitudes, 'b-', linewidth=2, marker='o', markersize=3, alpha=0.7)
    ax1.set_title('Изменение долготы от времени', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Время (секунды)', fontsize=12)
    ax1.set_ylabel('Долгота (градусы)', fontsize=12)
    ax1.grid(True, alpha=0.3)
    
    # Добавляем сетку и улучшаем читаемость
    ax1.tick_params(axis='both', which='major', labelsize=10)
    
    # 2. ГРАФИК: Траектория (широта vs долгота)
    ax2.plot(longitudes, latitudes, 'g-', linewidth=2, marker='s', markersize=3, alpha=0.7)
    ax2.set_title('Траектория полета', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Долгота (градусы)', fontsize=12)
    ax2.set_ylabel('Широта (градусы)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Отмечаем первую и последнюю точки
    ax2.plot(longitudes[0], latitudes[0], 'ro', markersize=8, label='Начало', zorder=5)
    ax2.plot(longitudes[-1], latitudes[-1], 'yo', markersize=8, label='Конец', zorder=5)
    ax2.legend()
    
    # Автоматически подбираем масштаб
    if len(longitudes) > 1:
        lon_range = max(longitudes) - min(longitudes)
        lat_range = max(latitudes) - min(latitudes)
        
        # Добавляем немного отступов
        ax2.set_xlim(min(longitudes) - 0.1*lon_range, max(longitudes) + 0.1*lon_range)
        ax2.set_ylim(min(latitudes) - 0.1*lat_range, max(latitudes) + 0.1*lat_range)
    
    # Общий заголовок
    plt.suptitle(f'Анализ полета - {filename}', fontsize=16, fontweight='bold', y=1.02)
    
    # Сохраняем
    output_name = f'{filename.split(".")[0]}_analysis.png'
    plt.tight_layout()
    plt.savefig(output_name, dpi=150, bbox_inches='tight')
    print(f"\nГрафики сохранены в файл: {output_name}")
    
    plt.show()
    
    return output_name

def print_statistics(times, latitudes, longitudes):
    """Выводим простую статистику"""
    print("\n" + "="*50)
    print("СТАТИСТИКА ПОЛЕТА")
    print("="*50)
    
    print(f"Количество точек: {len(times)}")
    print(f"Длительность полета: {times[-1] - times[0]:.2f} секунд")
    print(f"Частота обновления: {len(times) / (times[-1] - times[0]):.1f} точек/сек")
    
    print(f"\nКоординаты:")
    print(f"  Широта: от {min(latitudes):.6f}° до {max(latitudes):.6f}°")
    print(f"  Долгота: от {min(longitudes):.6f}° до {max(longitudes):.6f}°")
    
    # Определяем полушария
    east_points = sum(1 for lon in longitudes if lon > 0)
    west_points = sum(1 for lon in longitudes if lon < 0)
    
    print(f"\nРаспределение по полушариям:")
    print(f"  Восточное (lon > 0): {east_points} точек")
    print(f"  Западное (lon < 0): {west_points} точек")
    
    if east_points > 0 and west_points > 0:
        print(" Полёт пересекал нулевой меридиан")
    
    # Проверяем пересечение 180°
    has_180_crossing = False
    for i in range(1, len(longitudes)):
        if (longitudes[i-1] > 170 and longitudes[i] < -170) or \
           (longitudes[i-1] < -170 and longitudes[i] > 170):
            has_180_crossing = True
            print(f"  ✓ Обнаружен переход через линию перемены дат (~180°)")
            break

def main():
    """Основная функция"""
    # Автоматически ищем файл
    filename = "180M-E-Test.txt"
    
    try:
        # Парсим лог
        times, latitudes, longitudes = parse_piv_log(filename)
        
        if not times:
            print("В файле не найдены координаты!")
            return
        
        # Строим графики
        plot_simple_graphs(times, latitudes, longitudes, filename)
        
        # Выводим статистику
        print_statistics(times, latitudes, longitudes)
        
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
        print("Поместите файл лога в текущую директорию.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()