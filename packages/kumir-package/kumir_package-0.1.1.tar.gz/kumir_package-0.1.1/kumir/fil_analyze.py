import os
import sys


class FilAnalyzer:
    """
    Класс для анализа файлов формата .fil, используемых в KUMIR.
    """
    
    def __init__(self, file_path):
        """
        Инициализация анализатора файлов .fil
        
        Args:
            file_path (str): Путь к файлу .fil
        """
        self.file_path = file_path
        self.field_size = None
        self.robot_position = None
        self.special_fields = []
        self.point_a = None
        self.point_b = None
        
    def parse(self):
        """
        Парсинг файла .fil
        
        Returns:
            dict: Словарь с информацией о поле и объектах
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл {self.file_path} не найден")
        
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
        
        result = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Пропускаем пустые строки и комментарии без данных
            if not line or (line.startswith(';') and ':' not in line):
                continue
            
            # Обрабатываем размер поля
            if '; Field Size:' in line:
                next_line = lines[i+1].strip()
                x, y = map(int, next_line.split())
                self.field_size = (x, y)
                result['field_size'] = {'x': x, 'y': y}
            
            # Обрабатываем позицию робота
            elif '; Robot position:' in line:
                next_line = lines[i+1].strip()
                x, y = map(int, next_line.split())
                self.robot_position = (x, y)
                result['robot_position'] = {'x': x, 'y': y}
            
            # Обрабатываем специальные поля
            elif '; A set of special Fields:' in line:
                special_fields = []
                j = i + 1
                
                while j < len(lines) and not lines[j].strip().startswith('; End Of File'):
                    field_data = lines[j].strip().split()
                    if len(field_data) >= 9:  # Проверяем, что строка содержит данные поля
                        field = {
                            'x': int(field_data[0]),
                            'y': int(field_data[1]),
                            'wall': int(field_data[2]),
                            'color': int(field_data[3]),
                            'radiation': float(field_data[4]),
                            'temperature': float(field_data[5]),
                            'symbol': field_data[6],
                            'symbol1': field_data[7],
                            'point': field_data[8]
                        }
                        special_fields.append(field)
                        
                        # Обрабатываем точки А и Б
                        if field['symbol'] == 'А':
                            self.point_a = (field['x'], field['y'])
                        elif field['symbol'] == 'Б':
                            self.point_b = (field['x'], field['y'])
                        
                        if field['symbol1'] == 'А':
                            self.point_a = (field['x'], field['y'])
                        elif field['symbol1'] == 'Б':
                            self.point_b = (field['x'], field['y'])
                            
                    j += 1
                
                self.special_fields = special_fields
                result['special_fields'] = special_fields
        
        # Добавляем информацию о точках А и Б в результат
        if self.point_a:
            result['point_a'] = {'x': self.point_a[0], 'y': self.point_a[1]}
        if self.point_b:
            result['point_b'] = {'x': self.point_b[0], 'y': self.point_b[1]}
        
        return result
    
    def get_walls(self):
        """
        Получить список всех стен на поле
        
        Returns:
            list: Список координат стен
        """
        walls = []
        for field in self.special_fields:
            if field['wall'] > 0:
                walls.append((field['x'], field['y'], field['wall']))
        return walls
    
    def get_colored_cells(self):
        """
        Получить список всех окрашенных клеток
        
        Returns:
            list: Список окрашенных клеток с их цветами
        """
        colored = []
        for field in self.special_fields:
            if field['color'] > 0:
                colored.append((field['x'], field['y'], field['color']))
        return colored
    
    def get_point_a(self):
        """
        Получить координаты точки А
        
        Returns:
            tuple: Координаты точки А (x, y) или None, если точка не найдена
        """
        return self.point_a
    
    def get_point_b(self):
        """
        Получить координаты точки Б
        
        Returns:
            tuple: Координаты точки Б (x, y) или None, если точка не найдена
        """
        return self.point_b
