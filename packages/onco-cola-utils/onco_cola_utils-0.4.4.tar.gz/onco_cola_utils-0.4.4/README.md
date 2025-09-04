


# Onco-Cola's utils

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![GitHub last commit](https://img.shields.io/github/last-commit/VolodinAS/onco-cola-tools)

`onco-cola-utils` — это набор утилит для Python, предназначенный для упрощения работы с данными, особенно с файлами Excel. Библиотека включает инструменты для чтения, записи и обработки данных, а также вспомогательные модули для логирования, создания типизированных констант и форматированного вывода.

## Основные возможности

- **`ReaderController`**: Мощный класс для управления файлами Excel (XLS/XLSX). Позволяет читать данные, находить нужный лист, обновлять и сохранять файлы, а также добавлять уникальные идентификаторы к строкам.
- **`KeyParamClass`**: Метакласс для создания неизменяемых, enum-подобных классов. Идеально подходит для определения констант, статусов или других предопределенных значений в коде.
- **`pretty_print`**: Утилита для красивого вывода сложных объектов (dataclasses, словарей, списков), что упрощает отладку.
- **`logger`**: Преднастроенный логгер на базе `loguru` с цветовой кодировкой для разных уровней логирования (DEBUG, INFO, SUCCESS, ERROR).
- **`value_to_bool`**: Функция для преобразования различных значений в булев тип по расширенным правилам.

## Установка

Для установки зависимостей выполните команду:

```bash
pip install onco-cola-utils
```

> **Важно:** Перед запуском скриптов, работающих с Excel-файлами, убедитесь, что эти файлы не открыты в других программах, чтобы избежать ошибок доступа (`PermissionError`).

---




## API-документация

### `ReaderController`

Класс `ReaderController` предоставляет полный набор инструментов для взаимодействия с Excel-файлами. Он позволяет читать данные из листов, управлять их содержимым, проверять доступность файлов и сохранять изменения. Класс разработан с учетом удобства использования и автоматизации рутинных операций с табличными данными.

#### Инициализация

```python
ReaderController(file_path: Path, file_output: Path, is_new: bool = False, skip_rows: int = 0)
```

-   `file_path` (`Path`): Путь к входному Excel-файлу.
-   `file_output` (`Path`): Путь к выходному Excel-файлу. Может совпадать с `file_path`.
-   `is_new` (`bool`, по умолчанию `False`): Если `True`, файл считается новым и не проверяется на существование при инициализации.
-   `skip_rows` (`int`, по умолчанию `0`): Количество строк, которые нужно пропустить при чтении данных. (На данный момент не полностью реализовано в методах чтения).

**Пример:**

```python
from onco_cola_utils.reader_controller.core import ReaderController
from pathlib import Path

input_excel = Path("data/input.xlsx")
output_excel = Path("data/output.xlsx")

reader = ReaderController(file_path=input_excel, file_output=output_excel)
```

#### Методы

##### `read_data(sheet_name: Optional[str] = None) -> None`

Читает данные из указанного листа Excel-файла и сохраняет их во внутренний датафрейм (`_dataframe`). Все значения преобразуются в строки, а числа с плавающей точкой, являющиеся целыми, форматируются без десятичной части (например, `1.0` становится `1`).

-   `sheet_name` (`str | None`, по умолчанию `None`): Имя листа для чтения. Если `None`, читается первый лист.

**Пример:**

```python
reader.read_data(sheet_name="Sheet1")
# Или для первого листа:
reader.read_data()
```

##### `get_data(sheet_name: Optional[str] = None) -> list[dict]`

Лениво загружает данные из Excel-файла, если они еще не были загружены. Возвращает текущий внутренний датафрейм.

-   `sheet_name` (`str | None`, по умолчанию `None`): Имя листа для чтения, если данные еще не загружены.

**Возвращает:**

-   `list[dict]`: Список словарей, где каждый словарь представляет строку данных, а ключи — имена столбцов.

**Пример:**

```python
data = reader.get_data()
for row in data:
    print(row)
```

##### `perfect_data(data_list: DFType) -> dict`

Фильтрует входной список данных, исключая строки, в которых значение в столбце `ColumnStrings.DATA_ENTITY_TOBE` соответствует одному из "нулевых" значений, определенных в `System.NULLED`.

-   `data_list` (`DFType`): Список словарей, представляющих данные.

**Возвращает:**

-   `dict`: Словарь, где ключами являются `local_id` строк, а значениями — отфильтрованные данные.

**Пример:**

```python
clean_data = reader.perfect_data(reader.get_data())
```

##### `local_idfy(data_list: DFType) -> dict`

Присваивает уникальные идентификаторы (`local_id`) строкам данных на основе уже существующих `local_id` в данных. Этот метод создает внутреннее представление данных, индексированное по `local_id`.

-   `data_list` (`DFType`): Список словарей, содержащих данные, которые нужно индексировать.

**Возвращает:**

-   `dict`: Словарь, где ключами являются `local_id`, а значениями — соответствующие строки данных.

**Пример:**

```python
indexed_data = reader.local_idfy(reader.get_data())
```

##### `cycle_right_sheet() -> None`

Автоматически определяет и выбирает правильный лист в Excel-файле. Метод итерируется по листам, удаляя первый лист и пересохраняя файл, пока не найдет лист, содержащий обязательные поля (`source_name` и `url`). Это полезно, если файл содержит служебные или пустые листы в начале.

**Пример:**

```python
# Обычно вызывается автоматически при проверке local_id или чтении данных
reader.cycle_right_sheet()
```

##### `check_local_id(find_it: bool = True) -> bool`

Проверяет наличие столбца `local_id` в данных. Перед проверкой вызывает `cycle_right_sheet()` для определения корректного листа.

-   `find_it` (`bool`, по умолчанию `True`): Если `True`, метод проверяет именно наличие `local_id`. Если `False`, метод просто убеждается, что лист корректен и содержит данные.

**Возвращает:**

-   `bool`: `True`, если `local_id` найден (или лист корректен, если `find_it=False`), иначе `False`.

**Пример:**

```python
if not reader.check_local_id():
    print("Столбец local_id не найден, будет добавлен.")
    reader.process_local_idfying()
```

##### `process_local_idfying(field: str = ColumnStrings.DATA_LOCAL_ID) -> None`

Добавляет или обновляет столбец `local_id` в данных, присваивая последовательные целочисленные значения (начиная с 1). После обработки данные сохраняются обратно в файл.

-   `field` (`str`, по умолчанию `ColumnStrings.DATA_LOCAL_ID`): Имя столбца, который будет использоваться для `local_id`.

**Пример:**

```python
reader.process_local_idfying()
```

##### `update_dataframe_from_updated_dataframe(updated_dataframe: dict, updated_fields: list[str], field_id: str = "ID") -> Optional[bool]`

Обновляет основной датафрейм (`_dataframe`) на основе предоставленных обновленных данных. Этот метод используется для слияния результатов обработки (например, ответа от ИИ-модели) с исходными данными.

-   `updated_dataframe` (`dict`): Словарь, где ключи — это `ID` строк, а значения — словари с обновленными полями.
-   `updated_fields` (`list[str]`): Список имен полей, которые должны быть обновлены.
-   `field_id` (`str`, по умолчанию `"ID"`): Имя поля, используемого в качестве идентификатора строки в `updated_dataframe`.

**Возвращает:**

-   `Optional[bool]`: `True` в случае успешного обновления, `None` если `updated_dataframe` или `updated_fields` пусты.

**Пример:**

```python
ai_results = {
    1: {"category_asis": "Electronics", "remark": "1"},
    2: {"category_asis": "Books", "remark": None},
}
reader.update_dataframe_from_updated_dataframe(
    updated_dataframe=ai_results,
    updated_fields=["category_asis", "remark"]
)
```

##### `update_file(same_file: bool = True) -> bool`

Сохраняет текущее состояние внутреннего датафрейма (`_dataframe`) обратно в Excel-файл.

-   `same_file` (`bool`, по умолчанию `True`): Если `True`, данные сохраняются в `file_path`. Если `False`, данные сохраняются в `file_output`.

**Возвращает:**

-   `bool`: `True` в случае успешного сохранения.

**Пример:**

```python
reader.update_file() # Сохранить в исходный файл
reader.update_file(same_file=False) # Сохранить в выходной файл
```

##### `save_to_csv(same_file: bool = True) -> bool`

Сохраняет текущее состояние внутреннего датафрейма в CSV-файл. Расширение файла должно быть `.csv` в `file_path` или `file_output`.

-   `same_file` (`bool`, по умолчанию `True`): Если `True`, данные сохраняются в `file_path`. Если `False`, данные сохраняются в `file_output`.

**Возвращает:**

-   `bool`: `True` в случае успешного сохранения.

**Пример:**

```python
# Предполагается, что reader._file_output установлен на Path("data/output.csv")
reader.save_to_csv(same_file=False)
```

##### `rename(new_name: str, same_file: bool = True) -> bool`

Переименовывает входной или выходной файл Excel.

-   `new_name` (`str`): Новое базовое имя файла (без расширения).
-   `same_file` (`bool`, по умолчанию `True`): Если `True`, переименовывается `file_path`. Если `False`, переименовывается `file_output`.

**Возвращает:**

-   `bool`: `True` в случае успешного переименования.

**Пример:**

```python
reader.rename("processed_data")
```

##### `get_asis_fields() -> list[str]`

Возвращает список всех имен столбцов из текущего датафрейма, которые содержат подстроку `_asis`.

**Возвращает:**

-   `list[str]`: Отсортированный список имен столбцов.

**Пример:**

```python
asis_columns = reader.get_asis_fields()
print(asis_columns)
```

##### `get_tobe_fields() -> list[str]`

Возвращает список всех имен столбцов из текущего датафрейма, которые содержат подстроку `_tobe`.

**Возвращает:**

-   `list[str]`: Отсортированный список имен столбцов.

**Пример:**

```python
tobe_columns = reader.get_tobe_fields()
print(tobe_columns)
```

##### `idfy_to_dataframe(idfy_data: IdfyGoods) -> list[dict]`

Преобразует данные из формата `IdfyGoods` (словарь, индексированный по ID) обратно в список словарей, пригодный для использования с `pandas.DataFrame`.

-   `idfy_data` (`IdfyGoods`): Словарь данных, индексированный по ID.

**Возвращает:**

-   `list[dict]`: Список словарей, представляющих данные.

**Пример:**

```python
# Предположим, у нас есть данные в формате IdfyGoods
# indexed_data = reader.local_idfy(reader.get_data())
# df_format_data = reader.idfy_to_dataframe(indexed_data)
```

#### Свойства

-   `rows_total` (`int`): Общее количество строк в данных, включая заголовки (если применимо).
-   `rows_data` (`int`): Количество строк с данными (без заголовков).
-   `get_sheet_names() -> list[str]`: Возвращает список имен всех листов в Excel-файле.




### `KeyParamClass`

`KeyParamClass` — это базовый класс, который позволяет создавать неизменяемые, типобезопасные константы, похожие на `Enum`, но с дополнительными атрибутами `name` (короткое строковое имя) и `desc` (подробное описание). Это удобно для определения фиксированных наборов значений, таких как статусы, типы или категории, где помимо самого значения требуется и его человекочитаемое описание.

#### Использование

Для создания набора констант, унаследуйте свой класс от `KeyParamClass` и определите константы как кортежи `(name: str, desc: str)`.

```python
from onco_cola_utils.key_param_class.core import KeyParamClass

class Status(KeyParamClass):
    PENDING = ("pending", "Ожидает обработки")
    ACTIVE = ("active", "Активен")
    COMPLETED = ("completed", "Завершено")
    CANCELLED = ("cancelled", "Отменено")

# Доступ к константам
print(Status.PENDING)          # Вывод: pending (возвращает .name по умолчанию)
print(Status.ACTIVE.name)      # Вывод: active
print(Status.COMPLETED.desc)   # Вывод: Завершено

# Сравнение
print(Status.PENDING == "pending") # Вывод: True
print(Status.ACTIVE == Status.ACTIVE) # Вывод: True

# Итерация по всем константам
for status in Status:
    print(f"Имя: {status.name}, Описание: {status.desc}")

# Получение константы по имени или атрибуту
print(Status.from_name("active")) # Вывод: <Status.ACTIVE: active (Активен)>
print(Status.get("COMPLETED"))    # Вывод: <Status.COMPLETED: completed (Завершено)>

# Получение всех констант в виде списка кортежей (name, desc)
print(Status.choices) # Вывод: [("pending", "Ожидает обработки"), ("active", "Активен"), ...]

# Получение всех констант в виде словаря
print(Status.dict()) # Вывод: {"PENDING": {"name": "pending", "desc": "Ожидает обработки"}, ...}
```

#### Особенности

-   **Неизменяемость**: После создания экземпляры `KeyParamClass` и сам класс являются неизменяемыми. Попытка изменить их атрибуты вызовет `AttributeError`.
-   **Проверка дубликатов**: Метакласс проверяет уникальность `name` (кода) при определении констант. Дубликаты `desc` (описания) вызовут предупреждение, но не ошибку.
-   **Enum-like API**: Поддерживает методы, схожие с `Enum`, такие как итерация, доступ по ключу (`Status["PENDING"]`), `get()`, `from_name()`, `choices` и `dict()`.

---




### `pretty_print`

Модуль `pretty_print` предоставляет функцию для форматированного вывода сложных структур данных, таких как `dataclasses`, словари и списки. Это значительно улучшает читаемость вывода в консоли и упрощает отладку.

#### Функция `pretty_print`

```python
pretty_print(obj, indent: int = 4, title: str = 'PRETTY_PRINT', m2d: bool = False, outputter=log)
```

-   `obj`: Объект, который нужно вывести. Может быть `dataclass`, словарем, списком или другим типом.
-   `indent` (`int`, по умолчанию `4`): Количество пробелов для каждого уровня отступа.
-   `title` (`str`, по умолчанию `'PRETTY_PRINT'`): Заголовок, который будет выведен перед форматированным объектом.
-   `m2d` (`bool`, по умолчанию `False`): Если `True`, функция попытается преобразовать объект в словарь с помощью `model_to_dict` перед форматированием. Это полезно для объектов ORM или других моделей, которые могут быть преобразованы в словари.
-   `outputter` (`callable`, по умолчанию `log`): Функция, которая будет использоваться для вывода строк. По умолчанию используется функция `log` из встроенного модуля `logger`.

**Пример:**

```python
from dataclasses import dataclass
from onco_cola_utils.pretty_print.core import pretty_print

@dataclass
class User:
    name: str
    age: int
    contacts: dict

user_data = User(
    name="Alice",
    age=30,
    contacts={
        "email": "alice@example.com",
        "phone": "123-456-7890"
    }
)

pretty_print(user_data, title="User Profile")

# Вывод:
# User Profile
# User(
#     name='Alice',
#     age=30,
#     contacts={
#         'email': 'alice@example.com',
#         'phone': '123-456-7890',
#     },
# )

pretty_print({"item1": 10, "item2": ["a", "b"]}, title="My Dictionary")

# Вывод:
# My Dictionary
# dict(
#     'item1': 10,
#     'item2': [
#         'a',
#         'b',
#     ],
# )
```

---




### `logger`

Модуль `logger` предоставляет удобный и настраиваемый интерфейс для логирования событий в приложении, используя библиотеку `loguru`. Он преднастроен для вывода сообщений разных уровней с цветовой кодировкой в стандартный поток ошибок (`sys.stderr`).

#### Уровни логирования и функции

Модуль предоставляет следующие функции для логирования:

| Уровень   | Функция   | Описание                                        |
| :-------- | :-------- | :---------------------------------------------- |
| `DEBUG`   | `log`     | Для отладочной информации.                      |
| `INFO`    | `loginf`  | Для общей информации о ходе выполнения.         |
| `SUCCESS` | `logsuc`  | Для сообщений об успешном выполнении операций. |
| `ERROR`   | `logerr`  | Для сообщений об ошибках.                       |

**Пример:**

```python
from onco_cola_utils.logger.core import log, loginf, logsuc, logerr

log("Это отладочное сообщение.")
loginf("Приложение запущено.")
logsuc("Операция успешно завершена!")
logerr("Произошла критическая ошибка.")
```

---




### `value_to_bool`

Функция `value_to_bool` предоставляет надежный способ преобразования различных типов значений (строк, чисел, булевых) в булево значение, используя расширенный набор правил.

#### Функция `value_to_bool`

```python
value_to_bool(value: Any) -> bool
```

-   `value`: Любое значение, которое нужно преобразовать в булево.

**Правила преобразования:**

-   **`True`**: `True`, `1`, `"true"`, `"1"`, `"yes"`, `"on"`, `"+"`, `"ok"`, `"да"`, `"вкл"`, `"y"`, `"t"`, `"enable"`, `"enabled"` (регистронезависимо).
-   **`False`**: `False`, `0`, `None`, `""` (пустая строка), `" "` (строка из пробелов), `"false"`, `"0"`, `"no"`, `"off"`, `"-"`, `"нет"`, `"выкл"`, `"n"`, `"f"`, `"disable"`, `"disabled"`, `"null"`, `"none"` (регистронезависимо).
-   Числа с плавающей точкой: `0.0` -> `False`, любое другое число -> `True`.
-   Любое другое значение, которое не соответствует правилам `True` или `False`, будет преобразовано в `False`.

**Пример:**

```python
from onco_cola_utils.value_to_bool import value_to_bool

print(value_to_bool("true"))    # True
print(value_to_bool(1))         # True
print(value_to_bool("да"))      # True
print(value_to_bool("false"))   # False
print(value_to_bool(0))         # False
print(value_to_bool(None))      # False
print(value_to_bool(""))        # False
print(value_to_bool("random_text")) # False
```

---




## Конфигурация

Библиотека использует несколько конфигурационных файлов для определения системных констант и строковых значений столбцов. Эти константы централизуют часто используемые значения и имена полей, обеспечивая единообразие и упрощая поддержку кода.

### `System` (в `src/onco_cola_utils/configs/system.py`)

Класс `System` содержит общие системные константы, используемые в приложении.

-   `NULLED`: Список значений, которые считаются "нулевыми" или пустыми при обработке данных (например, `["", "0", "none"]`).
-   `FULL_SKIP`: Список значений, при наличии которых строка данных должна быть полностью пропущена.
-   `ID`: Имя поля по умолчанию, используемое в качестве идентификатора строки (по умолчанию `"ID"`).

**Пример использования:**

```python
from onco_cola_utils.configs.system import System

if data_item.get(ColumnStrings.DATA_ENTITY_TOBE) in System.NULLED:
    # Обработка нулевых значений
    pass
```

### `ColumnStrings` (в `src/onco_cola_utils/configs/column_strings.py`)

Класс `ColumnStrings` определяет стандартизированные имена для различных столбцов, используемых в Excel-файлах и внутренних структурах данных. Это помогает избежать "магических строк" и обеспечивает консистентность в именовании полей.

-   `DATA_LOCAL_ID`: Имя столбца для локального идентификатора строки (по умолчанию `"local_id"`).
-   `DATA_SOURCE_NAME`: Имя столбца, содержащего исходное имя или описание данных (по умолчанию `"source_name"`).
-   `DATA_URL`: Имя столбца для URL-адресов (по умолчанию `"url"`).
-   `RMK`: Имя столбца для заметок или пометок (по умолчанию `"remark"`).
-   `DATA_ENTITY_TOBE`: Имя столбца, используемого для проверки на "нулевое" значение (по умолчанию `"category_tobe"`).

**Пример использования:**

```python
from onco_cola_utils.configs.column_strings import ColumnStrings

local_id_field = ColumnStrings.DATA_LOCAL_ID
print(f"Имя поля для локального ID: {local_id_field}")
```

---




## Зависимости

Проект `onco-cola-tools` использует следующие основные библиотеки:

-   `pandas` (`>=1.5`): Для работы с табличными данными и Excel-файлами.
-   `openpyxl` (`>=3.0`): Бэкенд для чтения и записи `.xlsx` файлов в `pandas`.
-   `loguru` (`^0.7.3`): Для расширенного и удобного логирования.
-   `deprecated` (`>=1.2`): Для маркировки устаревших функций и методов.
-   `build` (`>=1.3.0`): Для сборки пакета.
-   `twine` (`>=6.1.0`): Для публикации пакета.
-   `tiktoken` (`>=0.11.0`): Для работы с токенами (вероятно, для интеграции с LLM).

Все зависимости указаны в файле `pyproject.toml`.

---




## Лицензия

Данный проект распространяется под лицензией MIT. Подробности см. в файле `LICENSE`.

---



