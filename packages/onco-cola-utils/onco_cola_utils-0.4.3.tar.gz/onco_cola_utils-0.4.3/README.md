# ExcelDataProcessor

Мощный и гибкий инструмент для обработки, анализа и модификации Excel-файлов с поддержкой структурированного логирования, валидации данных и удобного отображения сложных структур. Основной компонент — `ReaderController` — предназначен для автоматизации работы с XLS(X) файлами, содержащими табличные данные, особенно в контексте обработки данных с помощью ИИ-моделей.

---

## Особенности

- ✅ **Полная поддержка Excel (xls/xlsx)**: чтение, запись, переименование, удаление листов
- 🔍 **Автоматический поиск нужного листа** по ключевым полям (`source_name`, `url`)
- 🧹 **Очистка и фильтрация данных**: удаление пустых строк, работа с TTL-значениями
- 🔢 **Локальная идентификация строк** через `local_id` (устойчивая к перезаписям)
- 🔄 **Обновление данных по ID**: безопасное слияние результатов ИИ-обработки с исходным датафреймом
- 🛡️ **Потокобезопасность и проверка блокировок**: контроль доступа к файлам
- 📄 **Экспорт в CSV**: гибкое сохранение в альтернативных форматах
- 🧾 **Красивый вывод структур**: встроенная поддержка pretty-print для словарей, списков и dataclass
- 📋 **Цветное логирование**: интеграция с `loguru`, удобные уровни логов (DEBUG, INFO, SUCCESS, ERROR)

---

## Установка

Этот пакет предполагает использование как внутреннего модуля (например, в составе larger ETL- или AI-проекта). Для установки зависимостей:

```bash
pip install pandas openpyxl loguru deprecated
```

> ⚠️ Убедитесь, что файлы **не открыты в Excel**, иначе будет ошибка записи.

---

## Быстрый старт

```python
from onco_cola_utils.reader_controller.core import ReaderController
from pathlib import Path

# Пути к файлам
input_file = Path("data/input.xlsx")
output_file = Path("data/output.xlsx")

# Создаём контроллер
reader = ReaderController(file_path=input_file, file_output=output_file)

# Автоматически находит нужный лист и читает данные
reader.read_data()

# Получаем данные без пустых значений
clean_data = reader.perfect_data(reader.get_data())

# Обновляем поле из ИИ-ответа
ai_response = [
    {"ID": "1", "category_asis": "Electronics", "remark": "1"},
    {"ID": "2", "category_asis": "Books", "remark": None},
]

# Применяем изменения
reader.update_dataframe_from_updated_dataframe(
    updated_dataframe={1: ai_response[0], 2: ai_response[1]},
    updated_fields=["category_asis", "remark"]
)

# Сохраняем результат
reader.update_file()
```

---

## API-документация

### `ReaderController(file_path, file_output, is_new=False, skip_rows=0)`

Основной класс для управления Excel-файлами.

**Параметры:**
- `file_path` (`Path`): путь к входному файлу.
- `file_output` (`Path`): путь к выходному файлу (может совпадать).
- `is_new` (`bool`): флаг, указывающий, что файл новый (не требует проверки на существование).
- `skip_rows` (`int`): количество строк для пропуска при чтении (не реализовано напрямую, но может быть расширено).

**Пример:**
```python
rc = ReaderController(Path("in.xlsx"), Path("out.xlsx"))
```

---

### `read_data(sheet_name=None) -> None`

Читает данные из Excel-листа в формате списка словарей. Все значения преобразуются в строки (с обрезанием `.0` у целых чисел).

**Параметры:**
- `sheet_name` (`str | None`): имя листа. Если `None` — читается первый активный лист.

**Пример:**
```python
reader.read_data(sheet_name="Sheet1")
```

---

### `get_data(sheet_name=None) -> list[dict]`

Ленивое получение данных: если данные ещё не загружены — вызывает `read_data()`.

**Возвращает:**
- `list[dict]`: список строк в виде словарей (ключ — имя столбца).

**Пример:**
```python
data = reader.get_data()
```

---

### `perfect_data(data_list) -> dict`

Фильтрует данные, удаляя строки, где значение в поле `DATA_ENTITY_TOBE` является "нулевым" (согласно `System.NULLED`).

**Параметры:**
- `data_list` (`list[dict]`): входной список данных.

**Возвращает:**
- `dict`: словарь, индексированный `local_id`.

**Пример:**
```python
filtered = reader.perfect_data(reader.get_data())
```

---

### `local_idfy(data_list) -> dict`

Присваивает идентификаторы на основе существующего `local_id` из данных.

**Параметры:**
- `data_list` (`list[dict]`): список данных с полем `local_id`.

**Возвращает:**
- `dict`: словарь вида `{local_id: row_data}`.

**Пример:**
```python
idfy_data = reader.local_idfy(data_list)
```

---

### `cycle_right_sheet() -> None`

Циклически удаляет первые листы Excel-файла, пока не найдёт лист, содержащий поля `source_name` и `url`.

**Использование:**
- Полезно при наличии служебных листов в начале файла.
- Автоматически пересохраняет файл без ненужных листов.

**Пример:**
```python
reader.cycle_right_sheet()  # Вызывается автоматически в check_local_id
```

---

### `check_local_id(find_it=True) -> bool`

Проверяет, содержит ли первый лист поле `local_id`. Перед этим запускает `cycle_right_sheet`.

**Параметры:**
- `find_it` (`bool`): если `True`, проверяет наличие `local_id`; иначе просто проверяет корректность листа.

**Возвращает:**
- `bool`: `True`, если `local_id` найден.

**Пример:**
```python
if not reader.check_local_id():
    reader.process_local_idfying()
```

---

### `process_local_idfying(field=ColumnStrings.DATA_LOCAL_ID) -> None`

Добавляет `local_id` (1, 2, 3...) к каждой строке и сохраняет файл.

**Пример:**
```python
reader.process_local_idfying()
```

---

### `update_dataframe_from_updated_dataframe(updated_dataframe, updated_fields, field_id="ID") -> bool | None`

Обновляет основной датафрейм на основе словаря обновлённых данных (например, ответа ИИ).

**Параметры:**
- `updated_dataframe` (`dict[int, dict]`): словарь `{ID: {field: value}}`.
- `updated_fields` (`list[str]`): список полей для обновления.
- `field_id` (`str`): ключ, по которому идентифицируются строки (по умолчанию `"ID"`).

**Возвращает:**
- `True` при успехе, `None` при ошибках.

**Пример:**
```python
reader.update_dataframe_from_updated_dataframe(
    updated_dataframe={1: {"cat_asis": "NewCat"}},
    updated_fields=["cat_asis"]
)
```

---

### `update_file(same_file=True) -> bool`

Сохраняет текущий датафрейм обратно в Excel.

**Параметры:**
- `same_file` (`bool`): если `True`, перезаписывает `file_path`, иначе — `file_output`.

**Пример:**
```python
reader.update_file(same_file=False)  # Сохранить в output
```

---

### `save_to_csv(same_file=True) -> bool`

Сохраняет данные в формате CSV.

**Параметры:**
- `same_file` (`bool`): использовать `file_path` или `file_output`.

**Пример:**
```python
reader.save_to_csv()
```

---

### `rename(new_name, same_file=True) -> bool`

Переименовывает файл.

**Параметры:**
- `new_name` (`str`): новое имя без расширения.
- `same_file` (`bool`): переименовать входной или выходной файл.

**Пример:**
```python
reader.rename("processed_data")
```

---

### `get_asis_fields() -> list[str]`

Возвращает список всех столбцов, содержащих `_asis`.

**Пример:**
```python
asis_cols = reader.get_asis_fields()
```

---

### `get_tobe_fields() -> list[str]`

Возвращает список всех столбцов, содержащих `_tobe`.

**Пример:**
```python
tobe_cols = reader.get_tobe_fields()
```

---

### `idfy_to_dataframe(idfy_data) -> list[dict]`

Преобразует `idfy`-словарь обратно в список словарей (формат датафрейма).

**Параметры:**
- `idfy_data` (`dict`): словарь вида `{ID: data}`.

**Возвращает:**
- `list[dict]`: готовый для `DataFrame` список.

---

## pretty_print(obj, title='PRETTY_PRINT', m2d=False, outputter=log)

Форматированный вывод сложных объектов (словари, списки, dataclass).

**Параметры:**
- `obj`: объект для вывода.
- `title` (`str`): заголовок лога.
- `m2d` (`bool`): преобразовать объект в словарь (через `model_to_dict`) перед выводом.
- `outputter` (`callable`): функция вывода (по умолчанию `log`).

**Пример:**
```python
from your_package.pretty_print.core import pretty_print

pretty_print({"a": 1, "b": {"c": 2}}, title="DATA")
# Вывод:
# PRETTY_PRINT
# dict(
#     a='1',
#     b=dict(
#         c='2',
#     ),
# )
```

---

## Логирование

Используется `loguru` с цветным выводом и уровнями:

| Уровень | Функция | Цвет |
|--------|--------|------|
| DEBUG | `log("msg")` | Белый |
| INFO | `loginf("msg")` | Синий |
| SUCCESS | `logsuc("msg")` | Зелёный |
| ERROR | `logerr("msg")` | Красный |

**Пример:**
```python
logsuc("Файл успешно обработан")
logerr("Ошибка валидации данных")
```

---

## Конфигурация

### Системные константы (в `configs/system.py`)

- `System.NULLED`: значения, считаемые "пустыми" (например, `["", "0", "none"]`).
- `System.FULL_SKIP`: значения, при которых строка полностью пропускается.
- `System.ID`: имя поля по умолчанию для ID (`"ID"`).

### Строки столбцов (в `configs/column_strings.py`)

- `ColumnStrings.DATA_LOCAL_ID`: имя столбца `local_id`.
- `ColumnStrings.DATA_SOURCE_NAME`: имя столбца `source_name`.
- `ColumnStrings.DATA_URL`: имя столбца `url`.
- `ColumnStrings.RMK`: имя столбца для заметок (`remark`).
- `ColumnStrings.DATA_ENTITY_TOBE`: поле для проверки на "нулевое" значение.

---

## Зависимости

```txt
pandas>=1.3.0
openpyxl>=3.0.0
loguru>=0.7.0
deprecated>=1.2.0
```

> Убедитесь, что Excel-файлы **не открыты в Excel** во избежание `PermissionError`.

---

## Лицензия

UNLICENSED (внутренний проект). Для использования в других проектах — требуется согласование.

---

## Дополнительно

### Обработка ошибок

- `WrongSheetListError`: ни один лист не содержит обязательных полей.
- `ContentLengthError`: данные отсутствуют или пусты.
- `PermissionError`: файл заблокирован (открыт в Excel).
- `ValueError`: ошибка при перезаписи (несоответствие размеров).

### Рекомендации

- Всегда вызывайте `cycle_right_sheet()` перед работой с данными.
- Используйте `local_idfy` вместо устаревшего `idfy_data`.
- Для отладки используйте `show_local_idfy_dataframe()`.
```

---

Теперь вы можете просто скопировать этот текст и вставить его в файл `README.md` вашего проекта. Всё отформатировано, валидно и готово к использованию.