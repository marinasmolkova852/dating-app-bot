import os, sys

activate_this = '/home/a1123675/venv/bin/activate_this.py'
with open(activate_this) as f:
     exec(f.read(), {'__file__': activate_this})
    

import aiomysql
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import datetime as dt
import os

load_dotenv()  # Загружаем переменные окружения из .env файла

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Создаем пул подключений к базе данных"""
        self.pool = await aiomysql.create_pool(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            db=os.getenv('DB_NAME'),
            autocommit=True,
            minsize=5,
            maxsize=10
        )

    async def close(self):
        """Закрываем пул подключений"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
    
    async def user_send_list(self):
        """Получаем информацию о пользователях"""
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM users")
                return await cursor.fetchall()
    
    async def user_list(self):
        """Получаем информацию о пользователях"""
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT tg_id AS 'ID', username AS 'Никнейм', date_of_reg AS 'Добавлен' FROM users")
                return await cursor.fetchall()
    
    async def check_user(self, tg_id: int):
        """Проверяем информацию о пользователе по ID"""
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM users WHERE tg_id = %s", (tg_id,))
                return await cursor.fetchone()
    
    async def add_new_user(self, tg_id: int, username: str):
        """Добавляем нового пользователя"""
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                date_of_reg = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
                await cursor.execute("INSERT INTO users (tg_id, username, date_of_reg) VALUES (%s, %s, %s)", (tg_id, username, date_of_reg))
    
    async def check_profile_details(self, tg_id: int):
        """Проверяем информацию о пользователе по ID"""
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM profile_details WHERE tg_id = %s", (tg_id,))
                return await cursor.fetchone()
                
    async def add_new_profile_details(self, tg_id: int):
        """Добавляем детали для нового пользователя"""
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                date_operation = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
                await cursor.execute("INSERT INTO profile_details (tg_id, date_operation) VALUES (%s, %s)", (tg_id, date_operation))

    async def update_user_info(self, tg_id: int, username: str):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("UPDATE users SET username=%s WHERE tg_id = %s", (username, tg_id))
    
    async def admin_list(self):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM admins")
                return await cursor.fetchall()
    
    async def admin_send_list(self):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT a.tg_id AS 'ID', u.username AS 'Никнейм', a.date_add AS 'Добавлен' FROM admins AS a JOIN users AS u ON u.tg_id = a.tg_id")
                return await cursor.fetchall()
    
    async def check_admin(self, tg_id: int):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM admins WHERE tg_id = %s", (tg_id,))
                return await cursor.fetchone()
                
    async def tariff_list(self):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT name AS 'Наименование\nтарифа', price AS 'Цена', amount_matches AS 'Кол-во\nмэтчей' FROM tariffs")
                return await cursor.fetchall()
    
    async def check_tariff(self, tariff_id: int):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM tariffs WHERE id = %s", (tariff_id,))
                return await cursor.fetchone()
                
    async def add_new_payment(self, tg_id: int, description: str, amount: int, tariff_id: int):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                payment_date = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
                await cursor.execute("INSERT INTO payments (tg_id, description, amount, date, tariff_id) VALUES (%s, %s, %s, %s, %s)", (tg_id, description, amount, payment_date, tariff_id))
    
    async def check_ref_by_promo(self, promocode: str):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM referrals WHERE promocode = %s", (promocode,))
                referral = await cursor.fetchone()
                if referral:
                    return referral['tg_id']
                else:
                    return referral
    
    async def update_earned_money(self, tg_id: int, money: int):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("UPDATE referrals SET earned_money = (earned_money + %s) WHERE tg_id = %s", (money, tg_id))
                
    
    async def update_user_details(self, tg_id: int, tariff_id: int):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                tariff = await self.check_tariff(tariff_id)
                amount_matches = tariff.get('amount_matches')
                name = tariff.get('name')
                last_operation = f'Тариф пользователя был изменён на «{name}»'
                date_operation = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
                await cursor.execute("UPDATE profile_details SET tariff_id = %s, amount_matches = %s, last_operation = %s, date_operation = %s WHERE tg_id = %s", (tariff_id, amount_matches, last_operation, date_operation, tg_id))

    async def payment_list(self):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT u.username AS 'Покупатель', t.name AS 'Тариф', p.amount AS 'Сумма\nплатежа', p.date AS 'Дата\nплатежа' FROM payments AS p JOIN users AS u ON u.tg_id = p.tg_id JOIN tariffs AS t ON t.id = p.tariff_id ")
                return await cursor.fetchall()
    
    async def ban_user(self, tg_id: int, reason: str):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                date_add = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
                await cursor.execute("INSERT INTO black_list (tg_id, reason, date_add) VALUES (%s, %s, %s)", (tg_id, reason, date_add))

    async def black_list(self):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM black_list")
                return await cursor.fetchall()
    
    async def check_ref(self, tg_id: int):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT * FROM referrals WHERE tg_id = %s", (tg_id,))
                return await cursor.fetchone()
    
    async def add_new_ref(self, tg_id: int, promocode: str):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                create_date = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
                await cursor.execute("INSERT INTO referrals (tg_id, promocode, create_date) VALUES (%s, %s, %s)", (tg_id, promocode, create_date))
    
    async def ref_list(self):
        async with self.pool.acquire() as connection:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute("SELECT tg_id AS 'ID\nучастника', promocode AS 'Сгенерированный\nпромокод' FROM referrals")
                return await cursor.fetchall()
    
# Создаем экземпляр базы данных для использования в других модулях
db = Database()
