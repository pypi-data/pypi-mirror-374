import clickhouse_connect  # Импорт библиотеки для работы с ClickHouse
import logging
import json
from typing import List, Dict, Any  # Импорт типов для аннотации


# cannot store nested lists

def escape_sql_string(html_string: str) -> str:
    """
    Экранирует специальные символы в строке для безопасной вставки в SQL-запросы.

    Args:
        html_string (str): Исходная строка с HTML-разметкой или текстом

    Returns:
        str: Экранированная строка, безопасная для использования в SQL
    """
    if html_string is None:  # Проверка на None для корректной обработки пустых значений
        return "NULL"  # Возвращаем строку "NULL" для вставки в SQL

    # Последовательное экранирование специальных символов
    escaped = html_string.replace("\\", "\\\\")  # Замена \ на \\ для корректной обработки слешей
    escaped = escaped.replace("'", "''")  # Замена ' на '' для защиты от SQL-инъекций
    escaped = escaped.replace('"', '\\"')  # Замена " на \" для корректной работы с кавычками
    escaped = escaped.replace("\0", "\\0")  # Экранирование нулевого символа
    escaped = escaped.replace("\n", "\\n")  # Замена новой строки на \n
    escaped = escaped.replace("\r", "\\r")  # Замена возврата каретки на \r
    escaped = escaped.replace("\t", "\\t")  # Замена табуляции на \t

    return escaped  # Возвращаем экранированную строку

def merge_dicts(dict1, dict2):
    """
    Объединяет два словаря. Если есть повторяющиеся ключи, значения из dict2 перезапишут значения из dict1.

    :param dict1: Первый словарь
    :param dict2: Второй словарь
    :return: Новый объединённый словарь
    """
    merged = dict1.copy()  # Создаем копию первого словаря, чтобы не изменять исходные данные
    merged.update(dict2)  # Добавляем элементы из второго словаря
    return merged



def load_data_from_json(filename):
    with open(filename, 'r') as f:
        prices = json.load(f)
    return prices


def save_data_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)


def make_connection_string(host, username='default', password='', port=8123):
    return f"http://{username}:{password}@{host}:{port}/"


class ClickHouseJSONHandler:
    """Класс для работы с JSON-данными и их вставкой в ClickHouse."""

    #Инициализация клиента ClickHouse.
    def __init__(self, connection_string, database, table_name=None, json_as_string=False):
        self.connection_string = connection_string
        self.database_name = database
        self.table_name = table_name
        self.json_as_string = json_as_string
        self.client = self._get_client()
        self.create_table()

    def _get_client(self):
        try:
            return clickhouse_connect.get_client(dsn=self.connection_string, database=self.database_name)
        except Exception as e:
            logging.error(f"Error connecting to Clickhouse: {e}")
            return None

    def _ensure_connection(self):
        if self.client is None or not self.client.ping():
            logging.warning("Reconnecting to Clickhouse...")
            self.client = self._get_client()

    def create_table(self, table_name: str = None):
        """
        Создает таблицу в ClickHouse на основе заданной структуры.

        Args:
            table_name (str): Название таблицы
            structure (Dict[str, str]): Структура таблицы (колонки и типы)
        """
        if table_name is None:
            table_name = self.table_name
        self._ensure_connection()
        # Формируем строку с определением колонок
        # SQL-запрос для создания таблицы с движком MergeTree
        json_internal_type = 'JSON'
        if self.json_as_string :
            json_internal_type = 'String'
        query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id UUID DEFAULT generateUUIDv4(),
            __metatimestamp_timestamp DateTime DEFAULT now(),
            json Nullable({json_internal_type}) 
        ) ENGINE = MergeTree
        ORDER BY __metatimestamp_timestamp  
        '''
        self.client.command(query)  # Выполняем запрос

    def insert_json_data(self, table_name: str=None, json_data={}):
        """
        Вставляет одну или несколько записей JSON в указанную таблицу ClickHouse.

        Args:
            table_name (str): Название таблицы
            json_data (Union[Dict[str, Any], List[Dict[str, Any]]]): Одна или несколько JSON-записей
        """
        if table_name is None:
            table_name = self.table_name
        try:
            self._ensure_connection()

            # Приводим к списку, если передан один объект
            if isinstance(json_data, dict):
                json_data = [json_data]

            # Формируем строки VALUES
            values = []
            for record in json_data:
                json_str = json.dumps(record).replace("'", "\\'")
                values.append(f"('{json_str}')")

            # Склеиваем все записи в один VALUES-блок
            values_str = ",\n".join(values)

            query = f"""
            INSERT INTO {table_name} (json)
            VALUES
            {values_str}
            """

            try:
                self.client.command(query)
            except Exception as e:
                logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
                raise

        except Exception as e:
            logging.error(f"Ошибка при обработке JSON-данных: {e}")
            raise

        return True


def main():
    """Основная функция для демонстрации работы с ClickHouse."""
    # Создаем экземпляр обработчика с указанием хоста и базы данных
    connection_string = make_connection_string(host='192.168.192.42')
    table_name = "complex_json_data_test"
    handler = ClickHouseJSONHandler(connection_string, database='mart',table_name=table_name,
                                    json_as_string=True)

    json_data = load_data_from_json("../../../data/complex_data.json")

    # Вставляем данные в таблицу
    handler.insert_json_data(table_name, [json_data])
    print("Данные успешно вставлены в ClickHouse")


if __name__ == "__main__":
    main()  # Запуск основной функции при выполнении скрипта
