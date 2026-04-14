import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


def fetch_birth_data():
    """
    Извлекает данные о рождаемости из HTML-кода страницы
    """
    url = 'https://countrymeters.info/ru/World'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        html = response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при загрузке страницы: {e}")
        return None

    # Парсим HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Ищем таблицу с данными в div population_clock
    population_clock = soup.find('div', id='population_clock')
    if not population_clock:
        print("❌ Не найден блок population_clock")
        return None

    # Ищем все строки таблицы
    rows = population_clock.find_all('tr')

    born_today = None
    born_year = None

    for row in rows:
        # Ищем ячейку с названием показателя
        data_name_cell = row.find('td', class_='data_name')
        if data_name_cell:
            data_name = data_name_cell.get_text(strip=True)

            # Ищем ячейку со значением счетчика
            counter_cell = row.find('td', class_='counter')
            if counter_cell:
                # Внутри counter_cell есть div с id="cp7", "cp6" и т.д.
                counter_div = counter_cell.find('div')
                if counter_div:
                    value = counter_div.get_text(strip=True)

                    if 'Рождено сегодня' in data_name:
                        born_today = value
                        print(f"✅ Найдено: {data_name} = {value}")
                    elif 'Рождено в этом году' in data_name:
                        born_year = value
                        print(f"✅ Найдено: {data_name} = {value}")

    # Альтернативный поиск по ID, если не нашли через структуру
    if not born_today or not born_year:
        # Ищем по конкретным ID
        if not born_today:
            cp7 = soup.find('div', id='cp7')
            if cp7:
                born_today = cp7.get_text(strip=True)
                print(f"✅ Найдено через cp7: Рождено сегодня = {born_today}")

        if not born_year:
            cp6 = soup.find('div', id='cp6')
            if cp6:
                born_year = cp6.get_text(strip=True)
                print(f"✅ Найдено через cp6: Рождено в этом году = {born_year}")

    if not born_today and not born_year:
        print("❌ Не удалось найти данные о рождаемости")
        return None

    # Формируем результат
    data = {
        'born_today': born_today if born_today else 'Н/Д',
        'born_year': born_year if born_year else 'Н/Д',
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return data


def print_table(data):
    """
    Выводит данные в виде красивой таблицы
    """
    if not data:
        print("Нет данных для отображения.")
        return

    # Подготавливаем данные для таблицы
    headers = ["Показатель", "Значение", "Дата обновления"]
    rows = [
        ["Рождено сегодня", data['born_today'], data['update_time']],
        ["Рождено в этом году", data['born_year'], data['update_time']]
    ]

    # Вычисляем ширину столбцов
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Добавляем отступы
    col_widths = [w + 2 for w in col_widths]

    # Рисуем таблицу
    print("\n" + "=" * 70)
    print("📊 ДАННЫЕ О РОЖДАЕМОСТИ В МИРЕ".center(70))
    print("=" * 70)

    # Верхняя граница
    top_border = "┌" + "┬".join("─" * w for w in col_widths) + "┐"
    print(top_border)

    # Заголовки
    header_row = "│"
    for i, header in enumerate(headers):
        header_row += f" {header:<{col_widths[i] - 1}}│"
    print(header_row)

    # Разделитель
    separator = "├" + "┼".join("─" * w for w in col_widths) + "┤"
    print(separator)

    # Данные
    for row in rows:
        data_row = "│"
        for i, cell in enumerate(row):
            data_row += f" {str(cell):<{col_widths[i] - 1}}│"
        print(data_row)

    # Нижняя граница
    bottom_border = "└" + "┴".join("─" * w for w in col_widths) + "┘"
    print(bottom_border)

    print(f"\n📅 Данные актуальны на: {data['update_time']}")
    print("📍 Источник: countrymeters.info")
    print("💡 Примечание: Данные обновляются в реальном времени на сайте\n")


def save_to_file(data, filename=None):
    """
    Сохраняет данные в файл
    """
    if not data:
        return

    if not filename:
        filename = f'birth_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("ДАННЫЕ О РОЖДАЕМОСТИ В МИРЕ\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Рождено сегодня: {data['born_today']}\n")
        f.write(f"Рождено в этом году: {data['born_year']}\n")
        f.write(f"Дата получения данных: {data['update_time']}\n")
        f.write(f"Источник: countrymeters.info\n")

    print(f"💾 Данные сохранены в файл: {filename}")

    # Также сохраняем в CSV
    csv_filename = filename.replace('.txt', '.csv')
    with open(csv_filename, 'w', encoding='utf-8-sig') as f:
        f.write("Показатель,Значение,Дата обновления\n")
        f.write(f"Рождено сегодня,{data['born_today']},{data['update_time']}\n")
        f.write(f"Рождено в этом году,{data['born_year']},{data['update_time']}\n")

    print(f"💾 Данные также сохранены в CSV: {csv_filename}")


def main():
    print("🔄 Получение данных о рождаемости в мире...")
    print("⏳ Пожалуйста, подождите...\n")

    birth_data = fetch_birth_data()

    if birth_data:
        print_table(birth_data)
        save_to_file(birth_data)

        # Дополнительно: выводим просто текст для копирования
        print("\n📋 Текст для копирования:")
        print("-" * 50)
        print(f"Рождено сегодня: {birth_data['born_today']}")
        print(f"Рождено в этом году: {birth_data['born_year']}")
        print(f"Дата: {birth_data['update_time']}")
        print("-" * 50)
    else:
        print("\n❌ Не удалось получить данные.")
        print("\nВозможные причины:")
        print("1. Отсутствует интернет-соединение")
        print("2. Сайт временно недоступен")
        print("3. Изменилась структура страницы")


if __name__ == "__main__":
    main()