#!/usr/bin/env python3
"""
Универсальный тест для проверки пересечения всех границ:
- Экватор (3 теста: hwr_620, hwr_621, hwr_622)
- Гринвич (3 теста: hwr_630, hwr_631, hwr_632)  
- Линия дат (3 теста: hwr_633, hwr_634, hwr_635)
- Полюса (4 теста: hwr_636, hwr_637, hwr_638, hwr_639)
Всего: 15 тестов
"""

import subprocess
import re
import sys
import os
from datetime import datetime

def extract_gnss_params(line):
    """Извлечение параметров из GNSS сообщения"""
    params = {}
    
    # Широта
    lat_match = re.search(r'lat\s+(-?\d+\.\d+)', line)
    if lat_match:
        params['lat'] = float(lat_match.group(1))
    
    # Долгота
    lon_match = re.search(r'lon\s+(-?\d+\.\d+)', line)
    if lon_match:
        params['lon'] = float(lon_match.group(1))
    
    # Курс
    track_match = re.search(r'TRUE_TRACK\s+(-?\d+\.?\d*)\s*deg', line)
    if track_match:
        params['track'] = float(track_match.group(1))
    
    # Скорость
    speed_match = re.search(r'TRACK_VEL\s+(\d+\.?\d*)\s*kt', line)
    if speed_match:
        params['speed'] = float(speed_match.group(1))
    else:
        params['speed'] = 470.5
    
    return params

def detect_test_type(filename, initial_params):
    """Определение типа теста по имени файла и начальным параметрам"""
    filename_lower = filename.lower()
    
    # ===== ЭКВАТОР =====
    if 'eq-n' in filename_lower or 'eq_n' in filename_lower:
        return {
            'name': 'hwr_620_equator_south_to_north_test',
            'description': 'Проверка прямого пересечения экватора с юга на север по меридиану',
            'boundary': 'equator',
            'expected_dir': 'north',
            'lon_constant': True,
            'check_pole': False
        }
    elif 'eq-s' in filename_lower:
        return {
            'name': 'hwr_621_equator_north_to_south_test',
            'description': 'Проверка прямого пересечения экватора с севера на юг по меридиану',
            'boundary': 'equator',
            'expected_dir': 'south',
            'lon_constant': True,
            'check_pole': False
        }
    elif 'eq-d' in filename_lower:
        return {
            'name': 'hwr_622_equator_diagonal_sw_ne_test',
            'description': 'Проверка диагонального пересечения экватора с юго-запада на северо-восток',
            'boundary': 'equator',
            'expected_dir': 'northeast',
            'lon_constant': False,
            'check_pole': False
        }
    
    # ===== ГРИНВИЧ =====
    elif '0m-e.piv' in filename_lower and '0m-e-d' not in filename_lower:
        return {
            'name': 'hwr_630_greenwich_west_to_east_test',
            'description': 'Проверка прямого пересечения гринвича с запада на восток по параллели',
            'boundary': 'greenwich',
            'expected_dir': 'east',
            'lat_constant': True,
            'check_pole': False
        }
    elif '0m-w' in filename_lower:
        return {
            'name': 'hwr_631_greenwich_east_to_west_test',
            'description': 'Проверка прямого пересечения гринвича с востока на запад по параллели',
            'boundary': 'greenwich',
            'expected_dir': 'west',
            'lat_constant': True,
            'check_pole': False
        }
    elif '0m-e-d' in filename_lower:
        return {
            'name': 'hwr_632_greenwich_diagonal_nw_se_test',
            'description': 'Проверка диагонального пересечения гринвича с северо-запада на юго-восток',
            'boundary': 'greenwich',
            'expected_dir': 'southeast',
            'lat_constant': False,
            'check_pole': False
        }
    
    # ===== ЛИНИЯ ДАТ =====
    elif '180m-e' in filename_lower and '180-d' not in filename_lower:
        return {
            'name': 'hwr_633_dataline_west_to_east_test',
            'description': 'Проверка прямого пересечения линии дат с запада на восток',
            'boundary': 'dataline',
            'expected_dir': 'east',
            'lat_constant': True,
            'check_pole': False
        }
    elif '180m-w' in filename_lower:
        return {
            'name': 'hwr_634_dataline_east_to_west_test',
            'description': 'Проверка прямого пересечения линии дат с востока на запад',
            'boundary': 'dataline',
            'expected_dir': 'west',
            'lat_constant': True,
            'check_pole': False
        }
    elif '180-d' in filename_lower: 
        return {
            'name': 'hwr_635_dataline_diagonal_ne_sw_test',
            'description': 'Проверка диагонального пересечения линии дат с северо-востока на юго-запад',
            'boundary': 'dataline',
            'expected_dir': 'southwest',
            'lat_constant': False,
            'check_pole': False
        }
    
    # ===== ПОЛЮСА =====
    elif 'n.piv' == filename_lower:
        return {
            'name': 'hwr_636_north_crossing_test',
            'description': 'Проверка пересечения северного полюса',
            'boundary': 'north_pole',
            'expected_dir': 'north',
            'lat_constant': False,
            'check_pole': True
        }
    elif 'n-d' in filename_lower:
        return {
            'name': 'hwr_637_north_diagonal_test',
            'description': 'Проверка диагонального движения вблизи северного полюса',
            'boundary': 'north_pole',
            'expected_dir': 'northeast',
            'lat_constant': False,
            'check_pole': True
        }
    elif 's.piv' == filename_lower:
        return {
            'name': 'hwr_638_south_crossing_test',
            'description': 'Проверка пересечения южного полюса',
            'boundary': 'south_pole',
            'expected_dir': 'south',
            'lat_constant': False,
            'check_pole': True
        }
    elif 's-d' in filename_lower:
        return {
            'name': 'hwr_639_south_diagonal_test',
            'description': 'Проверка диагонального движения вблизи южного полюса',
            'boundary': 'south_pole',
            'expected_dir': 'southwest',
            'lat_constant': False,
            'check_pole': True
        }
    
    # Если не определили по имени, пробуем по параметрам
    if initial_params:
        lat = initial_params.get('lat', 0)
        lon = initial_params.get('lon', 0)
        
        # Проверка на экватор
        if -1 < lat < 1:
            dir_by_lat = 'north' if lat < 0 else 'south'
            return {
                'name': 'equator_crossing_test',
                'description': f'Пересечение экватора ({dir_by_lat})',
                'boundary': 'equator',
                'expected_dir': dir_by_lat,
                'lon_constant': True,
                'check_pole': False
            }
        # Проверка на гринвич
        elif -1 < lon < 1:
            dir_by_lon = 'east' if lon < 0 else 'west'
            return {
                'name': 'greenwich_crossing_test',
                'description': f'Пересечение гринвича ({dir_by_lon})',
                'boundary': 'greenwich',
                'expected_dir': dir_by_lon,
                'lat_constant': True,
                'check_pole': False
            }
        # Проверка на линию дат
        elif abs(abs(lon) - 180) < 1:
            dir_by_lon = 'east' if lon > 0 else 'west'
            return {
                'name': 'dataline_crossing_test',
                'description': f'Пересечение линии дат ({dir_by_lon})',
                'boundary': 'dataline',
                'expected_dir': dir_by_lon,
                'lat_constant': True,
                'check_pole': False
            }
        # Проверка на полюса
        elif abs(abs(lat) - 90) < 1:
            pole_type = 'north_pole' if lat > 0 else 'south_pole'
            return {
                'name': 'pole_crossing_test',
                'description': f'Пересечение {pole_type}',
                'boundary': pole_type,
                'expected_dir': 'unknown',
                'lat_constant': False,
                'check_pole': True
            }
    
    # По умолчанию
    return {
        'name': 'boundary_crossing_test',
        'description': 'Проверка пересечения границы',
        'boundary': 'unknown',
        'expected_dir': 'unknown',
        'lat_constant': False,
        'lon_constant': False,
        'check_pole': False
    }

def check_equator_crossing(test_type, lat_values, lon_values):
    """Проверка пересечения экватора"""
    if len(lat_values) < 2:
        return False, "Недостаточно данных"
    
    initial_lat = lat_values[0]
    final_lat = lat_values[-1]
    expected_dir = test_type['expected_dir']
    
    # Проверка направления
    if expected_dir == 'north':
        # Юг → Север: начальная широта < 0, конечная > 0
        if initial_lat < 0 and final_lat > 0:
            for i in range(len(lat_values)-1):
                if lat_values[i] < 0 and lat_values[i+1] >= 0:
                    return True, f"Экватор пересечен (юг → север) между измерениями {i} и {i+1}"
    
    elif expected_dir == 'south':
        # Север → Юг: начальная широта > 0, конечная < 0
        if initial_lat > 0 and final_lat < 0:
            for i in range(len(lat_values)-1):
                if lat_values[i] > 0 and lat_values[i+1] <= 0:
                    return True, f"Экватор пересечен (север → юг) между измерениями {i} и {i+1}"
    
    elif expected_dir == 'northeast':
        # Юго-запад → Северо-восток
        if initial_lat < 0 and final_lat > 0:
            for i in range(len(lat_values)-1):
                if lat_values[i] < 0 and lat_values[i+1] >= 0:
                    return True, f"Экватор пересечен (ЮЗ→СВ) между измерениями {i} и {i+1}"
    
    return False, "Экватор не пересечен"

def check_greenwich_crossing(test_type, lat_values, lon_values):
    """Проверка пересечения гринвича"""
    if len(lon_values) < 2:
        return False, "Недостаточно данных"
    
    initial_lon = lon_values[0]
    final_lon = lon_values[-1]
    expected_dir = test_type['expected_dir']
    
    # Запад → Восток
    if expected_dir in ['east', 'southeast']:
        if initial_lon < 0 and final_lon > 0:
            for i in range(len(lon_values)-1):
                if lon_values[i] < 0 and lon_values[i+1] >= 0:
                    if expected_dir == 'east':
                        return True, f"Гринвич пересечен (запад → восток) между измерениями {i} и {i+1}"
                    else:  # southeast
                        return True, f"Гринвич пересечен (СЗ→ЮВ) между измерениями {i} и {i+1}"
    
    # Восток → Запад
    elif expected_dir == 'west':
        if initial_lon > 0 and final_lon < 0:
            for i in range(len(lon_values)-1):
                if lon_values[i] > 0 and lon_values[i+1] <= 0:
                    return True, f"Гринвич пересечен (восток → запад) между измерениями {i} и {i+1}"
    
    return False, "Гринвич не пересечен"

def check_dataline_crossing(test_type, lat_values, lon_values):
    """Проверка пересечения линии дат"""
    if len(lon_values) < 2:
        return False, "Недостаточно данных"
    
    initial_lon = lon_values[0]
    final_lon = lon_values[-1]
    expected_dir = test_type['expected_dir']
    
    # Запад → Восток: 179.9° → -179.9°
    if expected_dir in ['east', 'southwest']:
        if initial_lon > 170 and final_lon < -170:
            for i in range(len(lon_values)-1):
                if lon_values[i] > 170 and lon_values[i+1] < -170:
                    if expected_dir == 'east':
                        return True, f"Линия дат пересечена (запад → восток) между измерениями {i} и {i+1}"
                    else:  # southwest
                        return True, f"Линия дат пересечена (СВ→ЮЗ) между измерениями {i} и {i+1}"
    
    # Восток → Запад: -179.9° → 179.9°
    elif expected_dir == 'west':
        if initial_lon < -170 and final_lon > 170:
            for i in range(len(lon_values)-1):
                if lon_values[i] < -170 and lon_values[i+1] > 170:
                    return True, f"Линия дат пересечена (восток → запад) между измерениями {i} и {i+1}"
    
    return False, "Линия дат не пересечена"

def check_pole_crossing(test_type, lat_values, lon_values, track_values):
    """Проверка пересечения полюса"""
    if len(lat_values) < 2:
        return False, "Недостаточно данных"
    
    initial_lat = lat_values[0]
    final_lat = lat_values[-1]
    boundary = test_type['boundary']
    
    # Северный полюс
    if boundary == 'north_pole':
        # Проверяем приближение к полюсу (широта близка к 90°)
        max_lat = max(lat_values)
        if max_lat > 89.5:
            # Ищем момент максимальной широты
            for i in range(1, len(lat_values)-1):
                if lat_values[i] > 89.5 and lat_values[i-1] < lat_values[i] > lat_values[i+1]:
                    # Проверяем изменение долготы (должен быть скачок)
                    lon_before = lon_values[i-1]
                    lon_after = lon_values[i+1] if i+1 < len(lon_values) else lon_values[i]
                    
                    # Проверяем изменение курса (должен измениться на ~180°)
                    if len(track_values) > i+1:
                        track_change = abs(track_values[i+1] - track_values[i-1])
                        if track_change > 170:
                            return True, f"Северный полюс достигнут (~{max_lat:.1f}°), курс изменился на {track_change:.0f}°"
                    
                    return True, f"Северный полюс достигнут (~{max_lat:.1f}°)"
    
    # Южный полюс
    elif boundary == 'south_pole':
        min_lat = min(lat_values)
        if min_lat < -89.5:
            for i in range(1, len(lat_values)-1):
                if lat_values[i] < -89.5 and lat_values[i-1] > lat_values[i] < lat_values[i+1]:
                    if len(track_values) > i+1:
                        track_change = abs(track_values[i+1] - track_values[i-1])
                        if track_change > 170:
                            return True, f"Южный полюс достигнут (~{min_lat:.1f}°), курс изменился на {track_change:.0f}°"
                    
                    return True, f"Южный полюс достигнут (~{min_lat:.1f}°)"
    
    return False, f"{'Северный' if boundary == 'north_pole' else 'Южный'} полюс не достигнут"

def check_boundary_crossing(test_type, lat_values, lon_values, track_values):
    """Основная функция проверки пересечения границы"""
    
    if not lat_values or not lon_values:
        return False, "Нет данных для анализа"
    
    boundary = test_type['boundary']
    
    if boundary in ['equator', 'equator_diagonal']:
        return check_equator_crossing(test_type, lat_values, lon_values)
    
    elif boundary == 'greenwich':
        return check_greenwich_crossing(test_type, lat_values, lon_values)
    
    elif boundary == 'dataline':
        return check_dataline_crossing(test_type, lat_values, lon_values)
    
    elif boundary in ['north_pole', 'south_pole']:
        return check_pole_crossing(test_type, lat_values, lon_values, track_values)
    
    return False, "Неизвестный тип границы"

def check_consistency(test_type, lat_values, lon_values):
    """Проверка постоянства координат (где ожидается)"""
    issues = []
    
    # Проверка постоянства долготы для экватора
    if test_type.get('lon_constant', False) and len(lon_values) > 1:
        lon_change = max(lon_values) - min(lon_values)
        if lon_change > 0.001:
            issues.append(f"Долгота изменяется: {lon_change:.6f}° (ожидалось постоянство)")
    
    # Проверка постоянства широты для гринвича/линии дат
    if test_type.get('lat_constant', False) and len(lat_values) > 1:
        lat_change = max(lat_values) - min(lat_values)
        if lat_change > 0.001:
            issues.append(f"Широта изменяется: {lat_change:.6f}° (ожидалось постоянство)")
    
    return issues

def run_test(piv_file):
    """Запуск теста с указанным PIV-файлом"""
    if not os.path.exists(piv_file):
        print(f"Ошибка: файл '{piv_file}' не найден!")
        return False
    
    # Определяем длительность теста в зависимости от типа
    filename = os.path.basename(piv_file).lower()
    
    # Для полюсов нужны более длительные тесты
    if 'n.piv' in filename or 's.piv' in filename or 'n-d' in filename or 's-d' in filename:  # ИЗМЕНЕНО: n-test/s-test -> n-d/s-d
        test_duration = 180  # 3 минуты для полюсов
    elif '180' in filename:
        test_duration = 90   # 1.5 минуты для линии дат
    else:
        test_duration = 60   # 1 минута для остальных
    
    cmd = [
        "./udp_sender",
        "-file", piv_file,
        "-piv",
        "-indy_piv", 
        "-on", "debug_tx_piv",
        "-once",
        "-stop", str(test_duration)
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate()
    
    # Анализ логов
    lat_values = []
    lon_values = []
    track_values = []
    initial_params = None
    
    for line in stdout.split('\n'):
        if 'PIV_ID GNSS' in line or 'GNSS ALT' in line:
            params = extract_gnss_params(line)
            
            if params.get('lat') is not None and params.get('lon') is not None:
                lat_values.append(params['lat'])
                lon_values.append(params['lon'])
                if params.get('track') is not None:
                    track_values.append(params['track'])
                
                if initial_params is None:
                    initial_params = params
    
    # Проверка результатов
    if len(lat_values) < 2 or len(lon_values) < 2:
        print("Ошибка: недостаточно GNSS данных для анализа!")
        return False
    
    # Определение типа теста
    filename = os.path.basename(piv_file)
    test_type = detect_test_type(filename, initial_params)
    
    # Проверка пересечения границы
    test_passed, boundary_result = check_boundary_crossing(test_type, lat_values, lon_values, track_values)
    
    # Проверка постоянства координат
    consistency_issues = check_consistency(test_type, lat_values, lon_values)
    
    # Вывод подробного отчета
    print(f"Тест: {test_type['name']}")
    print(f"Описание: {test_type['description']}")
    print(f"Файл: {filename}")
    print(f"Время: {datetime.now()}")
    print(f"Результат: {'ПРОЙДЕН' if test_passed else 'НЕ ПРОЙДЕН'}")
    print(f"Длительность: {test_duration} секунд")
    print("")
    
    print("НАЧАЛЬНЫЕ ПАРАМЕТРЫ:")
    if initial_params:
        print(f"  Широта: {initial_params.get('lat', 'N/A'):.6f}°")
        print(f"  Долгота: {initial_params.get('lon', 'N/A'):.6f}°")
        print(f"  Курс: {initial_params.get('track', 'N/A'):.1f}°")
        print(f"  Скорость: {initial_params.get('speed', 'N/A'):.1f} узлов")
    else:
        print("  Нет данных")
    
    print("")
    print("РЕЗУЛЬТАТЫ:")
    print(f"  Тип границы: {test_type['boundary']}")
    print(f"  Ожидаемое направление: {test_type['expected_dir']}")
    print(f"  {boundary_result}")
    print(f"  Начальная широта: {lat_values[0]:.6f}°")
    print(f"  Конечная широта: {lat_values[-1]:.6f}°")
    print(f"  Начальная долгота: {lon_values[0]:.6f}°")
    print(f"  Конечная долгота: {lon_values[-1]:.6f}°")
    
    # Статистика
    if len(lat_values) > 0:
        lat_change = lat_values[-1] - lat_values[0]
        print(f"  Изменение широты: {lat_change:+.6f}°")
    
    if len(lon_values) > 0:
        lon_change = lon_values[-1] - lon_values[0]
        print(f"  Изменение долготы: {lon_change:+.6f}°")
    
    # Вывод проблем с постоянством
    if consistency_issues:
        print("  ПРЕДУПРЕЖДЕНИЯ:")
        for issue in consistency_issues:
            print(f"    • {issue}")
    
    print("")
    if test_passed and not consistency_issues:
        print("ОШИБКИ: Нет")
    elif test_passed and consistency_issues:
        print(f"ОШИБКИ: Предупреждения: {', '.join(consistency_issues)}")
    else:
        print(f"ОШИБКИ: {boundary_result}")
    
    # Запись результатов
    result_text = "ПРОЙДЕН" if test_passed else "НЕ ПРОЙДЕН"
    
    with open("test_results.log", "a") as f:
        f.write(f"{datetime.now()} - {test_type['name']} - {filename} - {result_text}\n")
    
    return test_passed and not consistency_issues

def main():
    if len(sys.argv) != 2:
        print("Использование: python3 universal_boundary_test.py <piv-файл>")
        print("\nПоддерживаемые тесты:")
        print("  ЭКВАТОР:")
        print("    eq-N.piv / eq_N.piv      - hwr_620: юг→север")
        print("    eq-S.piv                 - hwr_621: север→юг")
        print("    eq-d.piv                 - hwr_622: ЮЗ→СВ (диагональ)")  
        
        print("  ГРИНВИЧ:")
        print("    0M-E.piv                 - hwr_630: запад→восток")
        print("    0M-W.piv                 - hwr_631: восток→запад")
        print("    0M-E-d.piv               - hwr_632: СЗ→ЮВ (диагональ)")
        
        print("  ЛИНИЯ ДАТ:")
        print("    180M-E.piv               - hwr_633: запад→восток")
        print("    180M-W.piv               - hwr_634: восток→запад")
        print("    180-d.piv                - hwr_635: СВ→ЮЗ (диагональ)")  
        
        print("  ПОЛЮСА:")
        print("    N.piv                    - hwr_636: северный полюс")
        print("    N-d.piv                  - hwr_637: диагональ у сев. полюса")  
        print("    S.piv                    - hwr_638: южный полюс")
        print("    S-d.piv                  - hwr_639: диагональ у юж. полюса")  
        
        print("\nПример: python3 universal_boundary_test.py eq-S.piv")
        sys.exit(1)
    
    piv_file = sys.argv[1]
    
    try:
        result = run_test(piv_file)
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\nТест прерван")
        sys.exit(130)
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()