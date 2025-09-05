import os, sys

activate_this = '/home/a1123675/venv/bin/activate_this.py'
with open(activate_this) as f:
     exec(f.read(), {'__file__': activate_this})

from dbutils.pooled_db import PooledDB
import datetime as dt
import pymysql


pool = PooledDB(
    creator=pymysql,
    maxconnections=10,
    mincached=2,
    blocking=True,
    host='localhost',
    user='a1123675_main_db',
    password='SFAetBH4',
    database='a1123675_main_db',
    cursorclass=pymysql.cursors.DictCursor,
)

def connect_db():
    """Получить соединение из пула (используется внутри модуля)."""
    return pool.connection()


# connection = pymysql.connect(
#     host='127.0.0.1',
#     port=3306,
#     user='a1123675_main_db',
#     password='SFAetBH4',
#     database='a1123675_main_db',
#     autocommit=False,
#     cursorclass=pymysql.cursors.DictCursor
    
# )


def check_user(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE tg_id = %s", (tg_id,))
            return cursor.fetchone()
    finally:
        connection.close()
    
    # cursor = connection.cursor()
    # cursor.execute("SELECT * FROM users WHERE tg_id = %s ", tg_id)
    # data = cursor.fetchone()
    # cursor.close()
    # return data
    
def add_new_user(tg_id, username):
    date_of_reg = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO users (tg_id, username, date_of_reg) VALUES (%s, %s, %s)", (tg_id, username, date_of_reg))
            connection.commit()
    finally:
        connection.close()


def check_admin(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM admins WHERE tg_id = %s", (tg_id,))
            return cursor.fetchone()
    finally:
        connection.close()
    

def check_blocked(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM black_list WHERE tg_id = %s", (tg_id,))
            return cursor.fetchone()
    finally:
        connection.close()


def check_form(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM form WHERE tg_id = %s", (tg_id,))
            return cursor.fetchone()
    finally:
        connection.close()


def check_tariff(tariff_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tariffs WHERE id = %s", (tariff_id,))
            return cursor.fetchone()
    finally:
        connection.close()


def select_tariff(name):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM tariffs WHERE name = %s", name)
            return cursor.fetchone()
    finally:
        connection.close()


def check_ref(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM referrals WHERE tg_id = %s", tg_id)
            return cursor.fetchone()
    finally:
        connection.close()

    
def check_promocode(promocode):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM referrals WHERE promocode = %s", promocode)
            return cursor.fetchone()
    finally:
        connection.close()
    


def check_payments(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM payments WHERE tg_id = %s", tg_id)
            return cursor.fetchall()
    finally:
        connection.close()


def check_user_profile_details(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM profile_details WHERE tg_id = %s", tg_id)
            return cursor.fetchone()
    finally:
        connection.close()



def add_form(tg_id, data):
    tuple_data = tuple(data.values())
    create_date = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
    form_data = (create_date, tg_id) + tuple_data
    sql_query = """
        INSERT INTO form 
        (
            create_date,
            tg_id, 
            name, 
            sex, 
            social, 
            birth_dt, 
            birth_place, 
            sign, location, 
            distance, 
            orientation, 
            searching, 
            status, 
            older_gap, younger_gap,
            min_older, max_older, 
            min_younger, max_younger, 
            gives, my_appearance, my_character, 
            gets, partner_appearance, partner_character, 
            interests, moral_values, about_me
        ) 
        VALUES 
        (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query, form_data)
            connection.commit()
    finally:
        connection.close()


def add_user_details(tg_id, tariff_id):
    current_tariff = check_tariff(tariff_id)
    amount_matches = current_tariff.get("amount_matches")
    last_operation = f'Тариф «{current_tariff.get("name")}» установлен'
    date_operation = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
    set_at = date_operation
    expires_at = (dt.datetime.now() + dt.timedelta(days=30)).strftime("%d.%m.%Y %H:%M:%S")
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO profile_details (tg_id, tariff_id, amount_matches, last_operation, date_operation, set_at, expires_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", (tg_id, tariff_id, amount_matches, last_operation, date_operation, set_at, expires_at))
            connection.commit()
    finally:
        connection.close()


def save_refresh_token(tg_id, refresh_token):
    expires_at = (dt.datetime.now() + dt.timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM user_sessions WHERE tg_id = %s", (tg_id,))
            data = cursor.fetchone()
            if data:
                cursor.execute("UPDATE user_sessions SET refresh_token=%s, expires_at=%s, updated_at=NOW() WHERE tg_id = %s", (refresh_token, expires_at, tg_id))
            else:
                cursor.execute("INSERT INTO user_sessions (tg_id, refresh_token, expires_at) VALUES (%s, %s, %s)", (tg_id, refresh_token, expires_at))
            connection.commit()
    finally:
        connection.close()


def check_valid_refresh_token(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT refresh_token, expires_at FROM user_sessions WHERE tg_id = %s", tg_id)
            data = cursor.fetchone()
            if data:
                if data.get("expires_at") > dt.datetime.now():
                    return data.get("refresh_token")
                else:
                    # Токен истёк
                    return None
            # Токен отсутствует
            return None
    finally:
        connection.close()
        

def delete_refresh_token(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM user_sessions WHERE tg_id = %s", (tg_id,))
            connection.commit()
    finally:
        connection.close()        


def delete_form(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM form WHERE tg_id = %s", (tg_id,))
            connection.commit()
    finally:
        connection.close()   


def delete_user_details(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM profile_details WHERE tg_id = %s", (tg_id,))
            connection.commit()
    finally:
        connection.close()   
  

def update_user_tariff(tg_id, tariff_id):
    current_tariff = check_tariff(tariff_id)
    amount_matches = current_tariff.get("amount_matches")
    date_operation = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
    set_at = date_operation
    expires_at = (dt.datetime.now() + dt.timedelta(days=30)).strftime("%d.%m.%Y %H:%M:%S")
    last_operation = f'Тариф «{current_tariff.get("name")}» установлен'
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE profile_details SET tariff_id = %s, amount_matches = %s, last_operation = %s, date_operation = %s, set_at = %s, expires_at = %s WHERE tg_id = %s", (tariff_id, amount_matches, last_operation, date_operation, set_at, expires_at, tg_id))
            connection.commit()
    finally:
        connection.close()   


def update_amount_matches(tg_id, amount_matches):
    last_operation = f'Списание мэтчей в количестве {amount_matches} шт'
    date_operation = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE profile_details SET amount_matches = (amount_matches - %s), last_operation = %s, date_operation = %s  WHERE tg_id = %s", (amount_matches, last_operation, date_operation, tg_id))
            connection.commit()
    finally:
        connection.close()


def add_new_promo_apply(tg_id, ref_id):
    date_apply = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO invited (tg_id, ref_id, date_apply) VALUES (%s, %s, %s)", (tg_id, ref_id, date_apply))
            connection.commit()
    finally:
        connection.close()


def count_promo_apply(ref_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM invited WHERE ref_id = %s", (ref_id,))
            return cursor.fetchone()
    finally:
        connection.close()

def match_list(tg_id):
    sql_query = """
        SELECT  
            p.tg_id,  
            p.name, 
            p.sex, 
            p.age, 
            p.social,
            p.orientation, 
            p.searching, 
            p.location,
            p.sign AS partner_sign,
            sc.relation_type,
            p.gives AS partner_gives,
            p.my_character AS partner_character,
            p.my_appearance AS partner_appearance,
            p.interests AS partner_interests,
            p.moral_values AS partner_moral_values,
            sc.compatibility_percent + CountMatchingInterests(my.interests, p.interests) + CheckMoralValuesMatch(my.moral_values, p.moral_values) AS result_compatibility,
            p.about_me
        FROM 
            (
                SELECT 
                    f.tg_id, 
                    f.name, 
                    f.sex, 
                    CalculateAge(f.birth_dt) AS age,
                    f.social,
                    f.orientation, 
                    f.searching, 
                    GetSearchCategory(f.searching) AS search, 
                    f.sign,
                    f.location,
                    s.id AS sign_id,
                    f.min_younger, 
                    f.max_younger, 
                    f.min_older, 
                    f.max_older,
                    f.gives,
                    f.my_character,
                    f.my_appearance,
                    f.interests,
                	f.moral_values,
                	f.about_me
                FROM form f
                LEFT JOIN signs s ON f.sign = s.sign AND f.sex = s.sex
            ) AS p
        JOIN 
            (
                SELECT 
                    f.tg_id,
                    f.sex, 
                    CalculateAge(f.birth_dt) AS age, 
                    f.orientation, 
                    f.searching, 
                    GetSearchCategory(f.searching) AS search, 
                    f.sign,
                    s.id AS sign_id,
                    f.min_older, 
                    f.max_older, 
                    f.min_younger, 
                    f.max_younger,
                    f.interests,
                    f.moral_values
                FROM form f
                LEFT JOIN signs s ON f.sign = s.sign AND f.sex = s.sex
                WHERE f.tg_id = %s
            ) AS my
        JOIN sign_compatibility AS sc ON sc.sign_one = my.sign_id AND sc.sign_two = p.sign_id
        WHERE 
            (
              (p.age >= (my.age - my.max_younger) AND p.age <= (my.age - my.min_younger))
                OR
              (p.age >= (my.age + my.min_older) AND p.age <= (my.age + my.max_older)))
            AND
            (
               (my.age >= (p.age - p.max_younger) AND my.age <= (p.age - p.min_younger)) 
              OR
               (my.age >= (p.age + p.min_older) AND my.age <= (p.age + p.max_older))
            )
            AND my.search = p.search
            AND 
            (
                (my.search = 1) OR
                (
                    (my.search = 2 OR my.search = 3)
                    AND
                    (
                        (my.orientation = 'Гетеросексуал' AND p.sex != my.sex) OR
                        (my.orientation = 'Гей' AND p.sex = 'Мужской' AND p.sex = my.sex) OR
                        (my.orientation = 'Лесбиянка' AND p.sex = 'Женский' AND p.sex = my.sex) OR
                        (my.orientation = 'Бисексуал' AND p.orientation = 'Бисексуал') OR 
                        (my.orientation = 'Бисексуал' AND p.orientation = 'Гей' AND my.sex = 'Мужской' AND p.sex = 'Мужской') OR
                        (my.orientation = 'Бисексуал' AND p.orientation = 'Лесбиянка' AND my.sex = 'Женский' AND p.sex = 'Женский') OR
                        (my.orientation = 'Бисексуал' AND p.orientation = 'Гетеросексуал' AND my.sex != p.sex)
                    )
                )
            )
            AND p.tg_id != my.tg_id
        ORDER BY result_compatibility DESC;
    """
    
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query, tg_id)
            matches = cursor.fetchall()
            
            for match in matches:
                cursor.execute("SELECT status FROM match_status WHERE tg_id = %s AND match_id = %s", (tg_id, match['tg_id']))
                status = cursor.fetchone()
                match['status'] = status['status'] if status else 'новый'
            
            return matches
    finally:
        connection.close()


def check_match_status(tg_id, match_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT status FROM match_status WHERE tg_id = %s AND match_id = %s", (tg_id, match_id))
            match_status = cursor.fetchone()
            if match_status:
                return match_status['status']
            else:
                return match_status
    finally:
        connection.close()


def update_match_status(tg_id, match_id, status):
    created_at = f'{dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'

    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT status FROM match_status WHERE tg_id = %s AND match_id = %s", (tg_id, match_id))
            match_status = cursor.fetchone()
            if match_status:
                cursor.execute("UPDATE match_status SET status = %s, created_at = %s WHERE tg_id = %s AND match_id = %s", (status, created_at, tg_id, match_id))
                connection.commit()
            else:
                cursor.execute("INSERT INTO match_status (tg_id, match_id, status, created_at) VALUES (%s, %s, %s, %s)", (tg_id, match_id, status, created_at))
                connection.commit()
            
    finally:
        connection.close()


def delete_match_status(tg_id):
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM match_status WHERE tg_id = %s", (tg_id,))
            cursor.execute("DELETE FROM match_status WHERE match_id = %s", (tg_id,))
            connection.commit()
    finally:
        connection.close()  
