# Часто задаваемые вопросы (FAQ) - NEONPAY

Частые вопросы и ответы о библиотеке NEONPAY.

## Содержание

1. [Общие вопросы](#общие-вопросы)
2. [Установка и настройка](#установка-и-настройка)
3. [Обработка платежей](#обработка-платежей)
4. [Обработка ошибок](#обработка-ошибок)
5. [Безопасность](#безопасность)
6. [Продакшн развертывание](#продакшн-развертывание)
7. [Решение проблем](#решение-проблем)

## Общие вопросы

### Что такое NEONPAY?

NEONPAY - это Python библиотека, которая упрощает интеграцию платежей Telegram Stars для разработчиков ботов. Она предоставляет единый API для множества библиотек ботов (Aiogram, Pyrogram, pyTelegramBotAPI и др.) и автоматически обрабатывает платежи.

### Какие библиотеки ботов поддерживаются?

NEONPAY поддерживает:
- **Aiogram** (Рекомендуется) - Современная асинхронная библиотека
- **Pyrogram** - Популярная MTProto библиотека
- **pyTelegramBotAPI** - Простая синхронная библиотека
- **python-telegram-bot** - Комплексная библиотека
- **Raw Telegram Bot API** - Прямые HTTP запросы

### Что такое Telegram Stars?

Telegram Stars - это встроенная виртуальная валюта Telegram, которую пользователи могут покупать и использовать для оплаты цифровых товаров и услуг в ботах. Она официально поддерживается Telegram и обеспечивает бесшовный опыт платежей.

### Бесплатно ли использовать NEONPAY?

Да, NEONPAY полностью бесплатна и с открытым исходным кодом. Вы платите только комиссию Telegram за обработку платежей Stars (обычно 5% от суммы транзакции).

## Установка и настройка

### Как установить NEONPAY?

```bash
# Базовая установка
pip install neonpay

# С конкретной библиотекой бота
pip install neonpay aiogram  # Для Aiogram
pip install neonpay pyrogram  # Для Pyrogram
```

### Как быстро начать?

```python
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

# Инициализация
neonpay = create_neonpay(bot_instance=ваш_бот)

# Создание этапа платежа
stage = PaymentStage(
    title="Премиум доступ",
    description="Разблокировать премиум функции",
    price=25,  # 25 Telegram Stars
)
neonpay.create_payment_stage("premium", stage)

# Обработка платежей
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        print(f"Платеж получен: {result.amount} звезд")
```

### Нужно ли настраивать webhook?

Нет, NEONPAY автоматически обрабатывает конфигурацию webhook для поддерживаемых библиотек. Для Raw API вам нужно настроить webhook вручную.

### Как выбрать правильную библиотеку бота?

**Для новых проектов:** Используйте **Aiogram** - она современная, хорошо документирована и имеет отличную поддержку async.

**Для существующих проектов:** Используйте любую библиотеку, которую вы уже используете. NEONPAY работает со всеми основными библиотеками.

## Обработка платежей

### Как создать разные варианты платежей?

```python
# Варианты донатов
donation_stages = [
    PaymentStage("Поддержка 1⭐", "Помочь боту работать", 1),
    PaymentStage("Поддержка 10⭐", "Поддержать разработку", 10),
    PaymentStage("Поддержка 50⭐", "Большая поддержка", 50),
]

# Цифровые продукты
product_stages = [
    PaymentStage("Премиум доступ", "30 дней премиум", 25),
    PaymentStage("Кастомная тема", "Персонализированная тема", 15),
]

# Добавить все этапы
for i, stage in enumerate(donation_stages):
    neonpay.create_payment_stage(f"donate_{i}", stage)

for i, stage in enumerate(product_stages):
    neonpay.create_payment_stage(f"product_{i}", stage)
```

### Как обрабатывать разные типы платежей?

```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        if result.stage_id.startswith("donate_"):
            # Обработать донат
            await handle_donation(result)
        elif result.stage_id.startswith("product_"):
            # Обработать покупку продукта
            await handle_product_purchase(result)
        else:
            # Обработать другие платежи
            await handle_other_payment(result)
```

### Можно ли настроить сообщения о платежах?

Да, вы можете настроить сообщение благодарности:

```python
neonpay = create_neonpay(
    bot_instance=bot,
    thank_you_message="🎉 Спасибо за покупку! Ваш продукт теперь активен."
)
```

### Как валидировать суммы платежей?

```python
@neonpay.on_payment
async def handle_payment(result):
    # Получить ожидаемую сумму для этого этапа
    stage = neonpay.get_payment_stage(result.stage_id)
    expected_amount = stage.price
    
    if result.amount != expected_amount:
        logger.warning(f"Несоответствие суммы: ожидалось {expected_amount}, получено {result.amount}")
        return
    
    # Обработать платеж
    await process_payment(result)
```

## Обработка ошибок

### Что происходит, если платеж не удался?

NEONPAY автоматически обрабатывает неудачные платежи и предоставляет подробную информацию об ошибках:

```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        # Платеж успешен
        await process_successful_payment(result)
    elif result.status == PaymentStatus.FAILED:
        # Платеж не удался
        await handle_payment_failure(result)
    elif result.status == PaymentStatus.PENDING:
        # Платеж в ожидании
        await handle_pending_payment(result)
```

### Как обрабатывать сетевые ошибки?

```python
async def safe_send_payment(user_id: int, stage_id: str):
    try:
        await neonpay.send_payment(user_id, stage_id)
    except PaymentError as e:
        logger.error(f"Ошибка платежа: {e}")
        await bot.send_message(user_id, "Платеж не удался. Попробуйте еще раз.")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        await bot.send_message(user_id, "Что-то пошло не так. Попробуйте позже.")
```

### Что если токен бота недействителен?

NEONPAY вызовет `ConfigurationError`, если токен бота недействителен:

```python
try:
    neonpay = create_neonpay(bot_instance=bot)
except ConfigurationError as e:
    print(f"Ошибка конфигурации: {e}")
    # Проверьте ваш токен бота
```

## Безопасность

### Как защитить токен бота?

Никогда не хардкодите токены в исходном коде:

```python
# ❌ Неправильно
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# ✅ Правильно
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
```

### Как валидировать права пользователей?

```python
async def safe_send_payment(user_id: int, stage_id: str):
    # Проверить, может ли пользователь делать платежи
    if not await user_can_pay(user_id):
        await bot.send_message(user_id, "У вас нет прав на совершение платежей.")
        return
    
    # Проверить, достиг ли пользователь лимита платежей
    if await user_payment_limit_reached(user_id):
        await bot.send_message(user_id, "Вы достигли лимита платежей.")
        return
    
    # Отправить платеж
    await neonpay.send_payment(user_id, stage_id)
```

### Как предотвратить мошенничество с платежами?

```python
class PaymentValidator:
    def __init__(self):
        self.user_payments = defaultdict(list)
        self.max_payments_per_hour = 5
    
    async def validate_payment(self, user_id: int, stage_id: str) -> bool:
        # Проверить частоту платежей
        now = time.time()
        recent_payments = [
            t for t in self.user_payments[user_id] 
            if now - t < 3600  # Последний час
        ]
        
        if len(recent_payments) >= self.max_payments_per_hour:
            return False
        
        # Проверить на подозрительные паттерны
        if await self.is_suspicious_user(user_id):
            return False
        
        return True
    
    async def record_payment(self, user_id: int):
        self.user_payments[user_id].append(time.time())
```

## Продакшн развертывание

### Как развернуть в продакшн?

1. **Используйте переменные окружения:**
```python
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
```

2. **Настройте правильное логирование:**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

3. **Используйте продакшн базу данных:**
```python
# Замените хранилище в памяти на базу данных
import asyncpg

async def store_payment(payment_data):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO payments (user_id, amount, stage_id, created_at) VALUES ($1, $2, $3, NOW())",
        payment_data['user_id'], payment_data['amount'], payment_data['stage_id']
    )
    await conn.close()
```

### Как мониторить платежи?

```python
class PaymentMonitor:
    def __init__(self):
        self.payment_stats = defaultdict(int)
    
    async def log_payment(self, result):
        self.payment_stats['total_payments'] += 1
        self.payment_stats['total_amount'] += result.amount
        
        # Логировать в базу данных
        await self.store_payment_log(result)
        
        # Отправлять оповещения при высоком объеме
        if self.payment_stats['total_payments'] % 100 == 0:
            await self.send_volume_alert()
    
    async def get_stats(self):
        return dict(self.payment_stats)
```

### Как обрабатывать высокий трафик?

```python
# Используйте пул соединений
import asyncpg

class DatabasePool:
    def __init__(self, database_url: str):
        self.pool = None
        self.database_url = database_url
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=10,
            max_size=20
        )
    
    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
```

## Решение проблем

### Платеж не отправляется

**Проверьте:**
1. Токен бота действителен
2. Пользователь запустил бота
3. Этап платежа существует
4. ID пользователя правильный

```python
# Отладка отправки платежа
async def debug_send_payment(user_id: int, stage_id: str):
    # Проверить, существует ли этап
    stage = neonpay.get_payment_stage(stage_id)
    if not stage:
        print(f"Этап {stage_id} не найден")
        return
    
    # Проверить, существует ли пользователь
    try:
        user = await bot.get_chat(user_id)
        print(f"Пользователь найден: {user.first_name}")
    except Exception as e:
        print(f"Пользователь не найден: {e}")
        return
    
    # Отправить платеж
    try:
        await neonpay.send_payment(user_id, stage_id)
        print("Платеж отправлен успешно")
    except Exception as e:
        print(f"Платеж не удался: {e}")
```

### Callback платежа не работает

**Проверьте:**
1. Декоратор `@neonpay.on_payment` правильно применен
2. Функция асинхронная
3. Бот запущен и получает обновления

```python
# Тест callback платежа
@neonpay.on_payment
async def test_payment_handler(result):
    print(f"Callback платежа сработал: {result}")
    # Добавьте точку останова здесь для отладки
```

### Бот не отвечает на команды

**Проверьте:**
1. Токен бота правильный
2. Бот запущен
3. Команды правильно зарегистрированы
4. Сетевое подключение

```python
# Тест подключения бота
async def test_bot():
    try:
        me = await bot.get_me()
        print(f"Бот работает: {me.first_name}")
    except Exception as e:
        print(f"Подключение к боту не удалось: {e}")
```

### Проблемы с подключением к базе данных

```python
# Тест подключения к базе данных
async def test_database():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.fetchval("SELECT 1")
        print(f"База данных подключена: {result}")
        await conn.close()
    except Exception as e:
        print(f"Подключение к базе данных не удалось: {e}")
```

## Частые проблемы

### "Этап платежа не найден"

Это происходит, когда вы пытаетесь отправить платеж для несуществующего этапа:

```python
# Проверить доступные этапы
stages = neonpay.list_payment_stages()
print(f"Доступные этапы: {list(stages.keys())}")

# Создать этап, если отсутствует
if "premium" not in stages:
    stage = PaymentStage("Премиум", "Премиум доступ", 25)
    neonpay.create_payment_stage("premium", stage)
```

### "Не удалось отправить инвойс"

Это обычно означает:
1. Токен бота недействителен
2. Пользователь не запустил бота
3. ID пользователя неправильный

```python
# Отладка отправки инвойса
async def debug_invoice(user_id: int, stage_id: str):
    try:
        # Проверить информацию о боте
        me = await bot.get_me()
        print(f"Бот: {me.first_name} (@{me.username})")
        
        # Проверить пользователя
        user = await bot.get_chat(user_id)
        print(f"Пользователь: {user.first_name} (@{user.username})")
        
        # Отправить платеж
        await neonpay.send_payment(user_id, stage_id)
    except Exception as e:
        print(f"Ошибка: {e}")
```

### "Callback платежа не срабатывает"

Убедитесь, что:
1. Функция декорирована `@neonpay.on_payment`
2. Функция асинхронная
3. Бот получает обновления

```python
# Тест регистрации callback
stats = neonpay.get_stats()
print(f"Callbacks зарегистрированы: {stats['registered_callbacks']}")
```

## Получение помощи

### Где можно получить помощь?

1. **Документация**: Проверьте папку [examples](../../examples/)
2. **Сообщество**: Присоединяйтесь к нашему [Telegram сообществу](https://t.me/neonpay_community)
3. **Проблемы**: Откройте issue на [GitHub](https://github.com/Abbasxan/neonpay/issues)
4. **Email**: Свяжитесь с поддержкой по [support@neonpay.com](mailto:support@neonpay.com)

### Как сообщить об ошибках?

При сообщении об ошибках, пожалуйста, включите:
1. Версию Python
2. Версию NEONPAY
3. Библиотеку бота и версию
4. Сообщение об ошибке и стек вызовов
5. Шаги для воспроизведения

### Как запросить функции?

Запросы функций приветствуются! Пожалуйста:
1. Проверьте, существует ли функция уже
2. Опишите случай использования
3. Предоставьте пример кода, если возможно
4. Откройте issue на GitHub

---

**Все еще есть вопросы? Проверьте папку [examples](../../examples/) или свяжитесь с поддержкой!**
