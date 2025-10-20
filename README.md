# 🏢 AssetFlow - Система учёта IT-оборудования

## 📋 Оглавление

- [Возможности](#возможности)
- [Технологии](#технологии)
- [Установка](#установка)
- [Структура проекта](#структура-проекта)
- [Документация системного аналитика](#-документация-системного-аналитика)
- [База данных](#база-данных)
- [Разработка](#разработка)

## 🚀 Возможности

- 📊 **Учёт оборудования** - полный цикл от поступления до списания
- 👥 **Управление сотрудниками** - назначение МОЛ (материально ответственных лиц)
- 📋 **Система заявок** - подача, согласование, отслеживание статусов
- 🛡️ **Безопасность** - разделение прав по группам пользователей
- 📈 **Статистика** - автоматический подсчёт активов по статусам

## 🛠 Технологии

- **Backend:** Django 5.0 + Python 3.11+
- **Database:** PostgreSQL + Django ORM
- **Frontend:** HTML5, CSS3, Django Templates
- **Security:** Django Auth, Groups, Permissions
- **Deployment:** готово к Docker-развёртыванию

## ⚡ Быстрая установка

```bash
# 1. Клонируй репозиторий
git clone https://github.com/Mekito4u/assetflow-inventory.git
cd assetflow-inventory

# 2. Установи зависимости
pip install -r requirements.txt

# 3. Настрой базу данных (создай БД assetflow в PostgreSQL)
# 4. Примени миграции
python manage.py migrate

# 5. Создай администратора
python manage.py createsuperuser

# 6. Загрузи тестовые данные
python manage.py seed_data

# 7. Запусти сервер
python manage.py runserver
```
Перейди по адресу http://localhost:8000


## 📁 Структура проекта

```
assetflow_project/                 # Корневая директория проекта
├── inventory/                     # Основное приложение
│   ├── management/
│   │   └── commands/             # Кастомные команды Django
│   │       ├── seed_data.py      # Скрипт загрузки тестовых данных
│   │       └── reset_data.py     # Скрипт очистки данных
│   ├── migrations/               # Миграции базы данных
│   ├── templates/               # HTML-шаблоны
│   │   └── inventory/
│   │       ├── base.html        # Базовый шаблон
│   │       ├── device_list.html # Страница оборудования
│   │       └── employee_devices.html # Страница сотрудника
│   ├── __init__.py
│   ├── admin.py                 # Конфигурация админ-панели
│   ├── apps.py
│   ├── models.py               # МОДЕЛИ: DeviceType, Employee, Device, Request
│   ├── tests.py
│   ├── urls.py                 # Маршруты приложения
│   └── views.py                # Контроллеры
├── assetflow_project/           # Настройки проекта
│   ├── __init__.py
│   ├── settings.py             # Основные настройки
│   ├── urls.py                 # Корневые маршруты
│   └── wsgi.py
├── .gitignore                  # Игнорируемые файлы Git
├── manage.py                   # Точка входа Django
├── README.md                   # Документация
└── requirements.txt            # Зависимости проекта
```

## 📊 Документация системного аналитика


### Use Case Diagram
*Файл: `docs/diagrams/use_case/assetflow_use_case.png`*

### Бизнес-процессы (BPMN)
**Процесс выдачи оборудования:**
*Файл: `docs/diagrams/bpmn/equipment_request.png`*

### Требования
- [Системные требования](/docs/requirements/system_requirements.md)

*Диаграммы созданы в ходе реального проектирования системы*

## 🗃 База данных

**Модели данных:**

- `DeviceType` - типы оборудования (Ноутбук, Монитор, Мышь)
- `Employee` - сотрудники компании с контактными данными
- `Device` - инвентарные единицы с статусами и историей
- `Request` - заявки на оборудование с workflow статусов

**Связи:**

- `Device` → `DeviceType` (ForeignKey)
- `Request` → `Employee` + `Device` (два ForeignKey)
- **Защита данных:** `on_delete=models.PROTECT` для критических связей

## 🎯 Использование

**Для администраторов:**

- Доступ через `/admin` с правами суперпользователя
- Управление оборудованием, сотрудниками, заявками
- Просмотр статистики в веб-интерфейсе

**Для разработчиков:**

```python
# Пример работы с API моделей
from inventory.models import Device, Employee

# Получить все доступное оборудование
available_devices = Device.objects.filter(status='available')

# Найти оборудование сотрудника
employee = Employee.objects.get(email='i.ivanov@company.ru')
their_devices = Device.objects.filter(request__employee=employee)
```

## 🔧 Разработка

**Кастомные команды:**

```python
# Загрузить демо-данные
python
manage.py
seed_data

# Очистить базу (кроме пользователей) 
python
manage.py
reset_data
```

**Тестовые данные:**

Система включает готовое "тестовое предприятие" с:

- 2 отделами (IT, QA)
- 4 типами оборудования
- 2 сотрудниками с заявками

## 📄 Лицензия

MIT License - свободное использование с указанием авторства

**Разработано с ❤️ для эффективного управления IT-активами**

