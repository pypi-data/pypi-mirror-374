from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Tuple


class ChatScreenshotGenerator:
    """
    Генератор скриншотов чата в стиле мессенджера
    """
    
    def __init__(self, width: int = 400, background_color: str = "#f5f5f5"):
        """
        Инициализация генератора
        
        Args:
            width: Ширина изображения
            background_color: Цвет фона
        """
        self.width = width
        self.background_color = background_color
        self.padding = 20
        self.message_margin = 10
        self.bubble_padding = 12
        self.max_message_width = int(width * 0.7)
        
        # Цвета для сообщений
        self.user_color = "#007AFF"  # Синий для пользователя
        self.bot_color = "#E5E5EA"   # Серый для бота
        self.user_text_color = "#FFFFFF"
        self.bot_text_color = "#000000"
        
        # Попытка загрузить шрифт
        self.font_size = 16
        self.font = self._load_font()
    
    def _load_font(self):
        """Загрузка шрифта"""
        try:
            # Попытка загрузить системный шрифт
            if os.name == 'nt':  # Windows
                return ImageFont.truetype("arial.ttf", self.font_size)
            else:  # Linux/Mac
                return ImageFont.truetype("/System/Library/Fonts/Arial.ttf", self.font_size)
        except:
            # Если не удалось загрузить, используем стандартный
            return ImageFont.load_default()
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """
        Перенос текста по словам
        
        Args:
            text: Исходный текст
            max_width: Максимальная ширина в пикселях
            
        Returns:
            Список строк
        """
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = self.font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _draw_message_bubble(self, draw: ImageDraw, text: str, x: int, y: int, 
                           is_user: bool = True) -> int:
        """
        Отрисовка пузыря сообщения
        
        Args:
            draw: Объект для рисования
            text: Текст сообщения
            x: Позиция X
            y: Позиция Y
            is_user: True если сообщение от пользователя
            
        Returns:
            Высота пузыря
        """
        # Цвета
        bubble_color = self.user_color if is_user else self.bot_color
        text_color = self.user_text_color if is_user else self.bot_text_color
        
        # Перенос текста
        lines = self._wrap_text(text, self.max_message_width - 2 * self.bubble_padding)
        
        # Вычисление размеров
        line_height = self.font_size + 4 
        text_height = len(lines) * line_height
        bubble_height = text_height + 2 * self.bubble_padding
        
        # Максимальная ширина строки
        max_line_width = 0
        for line in lines:
            bbox = self.font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            max_line_width = max(max_line_width, line_width)
        
        bubble_width = max_line_width + 2 * self.bubble_padding
        
        # Позиционирование
        if is_user:
            bubble_x = self.width - self.padding - bubble_width
        else:
            bubble_x = self.padding
        
        # Рисование пузыря
        draw.rounded_rectangle(
            [bubble_x, y, bubble_x + bubble_width, y + bubble_height],
            radius=18,
            fill=bubble_color
        )
        
        # Рисование текста
        text_y = y + self.bubble_padding
        for line in lines:
            draw.text(
                (bubble_x + self.bubble_padding, text_y),
                line,
                fill=text_color,
                font=self.font
            )
            text_y += line_height
        
        return bubble_height
    
    def generate_chat_screenshot(self, messages: List[Tuple[str, bool]], 
                                save_path: str) -> str:
        """
        Генерация скриншота чата
        
        Args:
            messages: Список кортежей (текст_сообщения, is_user)
                     is_user=True для сообщений пользователя, False для бота
            save_path: Путь для сохранения PNG файла
            
        Returns:
            Путь к созданному файлу
        """
        # Предварительный расчет высоты
        total_height = self.padding * 2
        
        for text, is_user in messages:
            lines = self._wrap_text(text, self.max_message_width - 2 * self.bubble_padding)
            line_height = self.font_size + 4
            message_height = len(lines) * line_height + 2 * self.bubble_padding
            total_height += message_height + self.message_margin
        
        # Создание изображения
        img = Image.new('RGB', (self.width, total_height), self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Отрисовка сообщений
        current_y = self.padding
        
        for text, is_user in messages:
            bubble_height = self._draw_message_bubble(draw, text, 0, current_y, is_user)
            current_y += bubble_height + self.message_margin
        
        # Сохранение PNG файла
        img.save(save_path, 'PNG')
        return save_path
    
    def generate_from_dialog_string(self, dialog_string: str, 
                                  save_path: str) -> str:
        """
        Генерация из строки диалога
        
        Args:
            dialog_string: Строка вида "-Привет\n-Привет\n-Как дела?\n-Хорошо"
            save_path: Путь для сохранения PNG файла
            
        Returns:
            Путь к созданному файлу
        """
        lines = dialog_string.strip().split('\n')
        messages = []
        
        for i, line in enumerate(lines):
            if line.startswith('-'):
                text = line[1:].strip()
                # Четные индексы - пользователь, нечетные - бот
                is_user = i % 2 == 0
                messages.append((text, is_user))
        
        return self.generate_chat_screenshot(messages, save_path)


def create_chat_screenshot(dialog_string: str, save_path: str, 
                          width: int = 400) -> str:
    """
    Быстрая функция для создания скриншота чата
    
    Args:
        dialog_string: Строка диалога "-Привет\n-Привет\n-Как дела?"
        save_path: Путь для сохранения PNG файла
        width: Ширина изображения
        
    Returns:
        Путь к созданному файлу
    """
    generator = ChatScreenshotGenerator(width=width)
    return generator.generate_from_dialog_string(dialog_string, save_path)


# Пример использования
if __name__ == "__main__":
    # Тестовый диалог
    test_dialog = """-Привет
-Привет
-Как дела?
-Хорошо, твои как?
-Тоже хорошо, спасибо!"""
    
    # Создание скриншота
    generator = ChatScreenshotGenerator()
    file_path = generator.generate_from_dialog_string(test_dialog, "test_chat.png")
    print(f"Скриншот сохранен: {file_path}")
