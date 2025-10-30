#!/usr/bin/env python3
"""
Криптовалютный бэкенд - симулятор для демонстрации мониторинга логов
"""

import requests
import time
import random
from datetime import datetime

# Локальный адрес Loki
LOKI_URL = "http://localhost:3100/loki/api/v1/push"
APP_NAME = "crypto-app"


class CryptoBackend:
    """Эмуляция работы криптовалютного бэкенда"""
    
    def __init__(self):
        self.cryptocurrencies = {
            'BTC': {'price': 65000, 'name': 'Bitcoin'},
            'ETH': {'price': 3500, 'name': 'Ethereum'},
            'SOL': {'price': 150, 'name': 'Solana'},
            'ADA': {'price': 0.45, 'name': 'Cardano'}
        }
        self.users = ['alice', 'bob', 'charlie', 'david', 'eve']
        self.is_running = False
    
    def update_crypto_prices(self):
        """Обновление цен криптовалют с реалистичными колебаниями"""
        for symbol, data in self.cryptocurrencies.items():
            # Случайное изменение цены от -3% до +3%
            change_percent = random.uniform(-0.03, 0.03)
            new_price = data['price'] * (1 + change_percent)
            data['price'] = round(new_price, 2)
    
    def simulate_trading_activity(self):
        """Симуляция торговых операций"""
        self.update_crypto_prices()
        
        user = random.choice(self.users)
        crypto = random.choice(list(self.cryptocurrencies.keys()))
        amount = round(random.uniform(0.001, 10), 6)
        transaction_type = random.choice(['buy', 'sell'])
        
        # Эмуляция ошибок в 15% случаев
        is_failed = random.random() < 0.15
        
        price = self.cryptocurrencies[crypto]['price']
        crypto_name = self.cryptocurrencies[crypto]['name']
        
        if not is_failed:
            message = (
                f"✓ Транзакция выполнена: пользователь {user} "
                f"{transaction_type} {amount} {crypto} ({crypto_name}) "
                f"по цене ${price:.2f}"
            )
            self.send_log_to_loki(message, "trading", "INFO")
        else:
            error_reasons = [
                "Недостаточно средств",
                "Превышен лимит транзакций",
                "Временный сбой API биржи",
                "Ошибка валидации данных"
            ]
            reason = random.choice(error_reasons)
            message = (
                f"✗ Ошибка транзакции: {user} не смог {transaction_type} "
                f"{amount} {crypto}. Причина: {reason}"
            )
            self.send_log_to_loki(message, "trading", "ERROR")
    
    def simulate_user_activity(self):
        """Симуляция пользовательской активности"""
        user = random.choice(self.users)
        activities = [
            (f"Пользователь {user} вошел в систему", "INFO"),
            (f"Пользователь {user} обновил профиль", "INFO"),
            (f"Пользователь {user} запросил историю транзакций", "DEBUG"),
            (f"Попытка входа с неверным паролем для {user}", "WARNING"),
            (f"Пользователь {user} превысил лимит запросов API", "WARNING")
        ]
        
        message, level = random.choice(activities)
        self.send_log_to_loki(message, "user-activity", level)
    
    def simulate_system_events(self):
        """Симуляция системных событий"""
        events = [
            ("Синхронизация с блокчейном завершена успешно", "INFO"),
            ("Обновление курсов валют", "DEBUG"),
            ("Запущено резервное копирование базы данных", "INFO"),
            ("Обнаружена подозрительная активность в сети", "WARNING"),
            ("Высокая нагрузка на сервер", "WARNING"),
            ("Критическая ошибка: потеря соединения с БД", "CRITICAL")
        ]
        
        message, level = random.choice(events)
        self.send_log_to_loki(f"🔧 Система: {message}", "system", level)
    
    def simulate_validation_events(self):
        """Симуляция валидации данных"""
        user = random.choice(self.users)
        validations = [
            (f"Валидация данных пользователя {user} прошла успешно", "INFO"),
            (f"Обнаружены некорректные данные от {user}", "ERROR"),
            (f"Проверка лимитов для {user}", "DEBUG"),
            (f"Предупреждение: подозрительная активность {user}", "WARNING")
        ]
        
        message, level = random.choice(validations)
        self.send_log_to_loki(message, "validation", level)
    
    def send_log_to_loki(self, message: str, activity_type: str, level: str = "INFO"):
        """
        Отправляет лог в Loki через POST на /loki/api/v1/push
        
        Args:
            message: Текст сообщения лога
            activity_type: Тип активности (trading, user-activity, system, validation)
            level: Уровень логирования (INFO, ERROR, DEBUG, WARNING, CRITICAL)
        """
        # Timestamp в наносекундах (требование Loki)
        timestamp = str(int(time.time() * 1_000_000_000))
        
        # Формируем payload согласно API Loki
        payload = {
            "streams": [
                {
                    "stream": {
                        "job": APP_NAME,           # Константное имя приложения
                        "level": level,            # Уровень логирования
                        "activity": activity_type  # Тип активности
                    },
                    "values": [
                        [timestamp, message]
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(LOKI_URL, json=payload, timeout=5)
            
            if response.status_code == 204:
                # 204 No Content - успешная отправка в Loki
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level:8}] {message}")
            else:
                print(f"✗ Ошибка отправки в Loki: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ Не удается подключиться к Loki. Проверьте что контейнер запущен.")
        except requests.exceptions.Timeout:
            print(f"✗ Таймаут при отправке в Loki")
        except Exception as e:
            print(f"✗ Неожиданная ошибка: {e}")
    
    def run_continuous_simulation(self):
        """Непрерывная симуляция работы бэкенда"""
        self.is_running = True
        
        print("\n" + "="*70)
        print("🚀 Криптовалютный бэкенд запущен")
        print("="*70)
        print(f"📡 Отправка логов в: {LOKI_URL}")
        print(f"📊 Приложение: {APP_NAME}")
        print("🔄 Для остановки нажмите Ctrl+C")
        print("="*70 + "\n")
        
        # Даем Docker время на старт
        print("⏳ Ожидание готовности Loki (5 секунд)...\n")
        time.sleep(5)
        
        # Отправляем стартовое событие
        self.send_log_to_loki(
            "🎉 Криптовалютный бэкенд успешно запущен", 
            "system", 
            "INFO"
        )
        
        iteration = 0
        
        while self.is_running:
            try:
                iteration += 1
                
                # Выбираем случайный тип активности с весами
                activity_type = random.choices(
                    ['trading', 'user-activity', 'system', 'validation'],
                    weights=[0.5, 0.25, 0.15, 0.1],  # Больше торговых операций
                    k=1
                )[0]
                
                # Генерируем событие выбранного типа
                if activity_type == 'trading':
                    self.simulate_trading_activity()
                elif activity_type == 'user-activity':
                    self.simulate_user_activity()
                elif activity_type == 'system':
                    self.simulate_system_events()
                elif activity_type == 'validation':
                    self.simulate_validation_events()
                
                # Каждые 20 итераций показываем статистику
                if iteration % 20 == 0:
                    print(f"\n📊 Отправлено логов: {iteration}\n")
                
                # Случайная задержка между событиями (1-5 секунд)
                delay = random.uniform(1, 5)
                time.sleep(delay)
                
            except KeyboardInterrupt:
                print("\n\n⏹  Получен сигнал остановки...")
                self.is_running = False
                break
            except Exception as e:
                error_msg = f"Критическая ошибка в симуляции: {str(e)}"
                self.send_log_to_loki(error_msg, "system", "CRITICAL")
                print(f"\n❌ {error_msg}")
                time.sleep(5)
        
        # Отправляем финальное событие
        self.send_log_to_loki(
            "👋 Криптовалютный бэкенд остановлен", 
            "system", 
            "INFO"
        )
        
        print("\n" + "="*70)
        print("✅ Приложение успешно остановлено")
        print("="*70 + "\n")


def main():
    """Точка входа в приложение"""
    backend = CryptoBackend()
    backend.run_continuous_simulation()


if __name__ == "__main__":
    main()


