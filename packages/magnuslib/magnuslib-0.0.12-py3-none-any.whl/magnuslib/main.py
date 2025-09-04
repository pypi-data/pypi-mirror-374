import os
import pandas as pd
import shutil
import copy
import pythoncom
from datetime import date
pythoncom.CoInitializeEx(0)
import win32com.client
import io
import msoffcrypto
import time
# блок импорта отправки почты
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

from functools import wraps
import time

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

def retry(times, sec_):
    """декоратор для times-повторного выполнения функции при неудачном выполнении

    Args:
        times (_type_): попыток
        sec_ (_type_): секунд между попытками
    """

    def wrapper_fn(f):
        @wraps(f)
        def new_wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    print('---ПОПЫТКА ЧТЕНИЯ ФАЙЛА ---- %s' % (i + 1))
                    return f(*args, **kwargs)
                except Exception as e:
                    error = e
                    print(time.sleep(sec_))
            raise error

        return new_wrapper

    return wrapper_fn


@retry(10, 5)
def links_main(name_column_key, name_column_result, name_file, key, sep=';'):
    """функция для работы с путями, ссылки, вводные данные хранятся в блокноте

    Args:
        name_column_key (str): имя колонки с ключами
        name_column_result (str): имя колонки с результатами val
        name_file (_type_): имя файла (пример-file_links.txt)
        key (_type_): имя ключа
        sep (str): разделитель в докумнте (';',':')

    Returns:
        _type_: _description_
    """
    try:
        file = pd.read_csv(name_file, sep=sep)
        result = list(file[file[name_column_key] == key][name_column_result])[0]
        return result
    except Exception as ex_:
        print(
            f'ошибка функции {links_main.__name__} не удалось считать файл {name_file} или данные в нем {key} ошибка {ex_}')


def dir_link():
    """возвращает абсолютный путь в (.py .ipynp)
    """

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return script_dir
    except:
        script_dir_2 = os.getcwd()
        return script_dir_2



def yesterday(days: int = 1):
    """возвращает дату на вчера - по уморлчанию минус 1 день

    Args:
        days (int, optional): на сколько дней назад откатываемся по дате. Defaults to 1.

    Returns:
        _type_: _description_
    """

    try:

        date = datetime.now()
        new_date = date - timedelta(days=days)  # вычитание одного дня
        return new_date
    except Exception as ex_:
        print(f'ошибка функции {yesterday.__name__}  {ex_}')


def create_date(year:int, month:int, day:int=1):

    """
    Создает объект даты по году и месяцу.
  
    Args:
      year: Год (целое число).
      month: Месяц (целое число от 1 до 12).
  
    Returns:
      Объект datetime.date, представляющий первый день указанного месяца и года.
    """
    try:
        return date(year, month, day)
    except Exception as ex_:
        print(f'ошибка функции {create_date.__name__}  {ex_}')


def converter_month_to_int(word, param='long' or 'short'):
    try:
        if param == 'short':
            word_ = word.lower()
            if 'янв' in word_:
                return 1
            elif 'фев' in word_:
                return 2
            elif 'мар' in word_:
                return 3
            elif 'апр' in word_:
                return 4
            elif 'май' in word_:
                return 5
            elif 'июн' in word_:
                return 6
            elif 'июл' in word_:
                return 7
            elif 'авг' in word_:
                return 8
            elif 'сен' in word_:
                return 9
            elif 'окт' in word_:
                return 10
            elif 'ноя' in word_:
                return 11
            elif 'дек' in word_:
                return 12
            else:
                return f'{word} не распознано'
        elif param == 'long':
            word_ = word.lower()
            if 'январь' in word_:
                return 1
            elif 'февраль' in word_:
                return 2
            elif 'мар' in word_:
                return 3
            elif 'апрель' in word_:
                return 4
            elif 'май' in word_:
                return 5
            elif 'июнь' in word_:
                return 6
            elif 'июль' in word_:
                return 7
            elif 'август' in word_:
                return 8
            elif 'сентябрь' in word_:
                return 9
            elif 'октябрь' in word_:
                return 10
            elif 'ноябрь' in word_:
                return 11
            elif 'декабрь' in word_:
                return 12
            else:
                return f'{word} не распознано'
        else:
            print(f'Не указан обязательный параметр функции - param (long or short)')
    except Exception as ex_:
            print(f'ошибка функции {converter_month_to_int.__name__}  {ex_}')


def last_day_of_month(year:int, month:int):

    """
    Возвращает последний день указанного месяца и года.
  
    Args:
      year: Год.
      month: Месяц (1-12).
  
    Returns:
      Последний день месяца.
    """
    try:
        return calendar.monthrange(year, month)[1]
    except Exception as ex_:
        print(f'ошибка функции {last_day_of_month.__name__}  {ex_}')


def convert_str_to_datetime(year, month, day):
    """конвертирует str date в datetime

    Args:
        year (_type_): _description_
        month (_type_): _description_
        day (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:

        date_object = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()
        return date_object
    except Exception as ex_:
        print(f'ошибка функции {convert_str_to_datetime.__name__}  {ex_}')


def date_start_stop(year, month):
    """возвращает начало и конец периода в формате YYYY-MM-DD

    Args:
        year (int): _description_
        month (int): _description_

    Returns:
        tuple(date:str, date:str): ('2025-07-01', '2025-07-31')
    """
    try:
        start_date = create_date(year, month)
        start_date_ret = f'{start_date.year}-{"0" + str(start_date.month) if len(str(start_date.month)) == 1 else start_date.month}-{"0" + str(start_date.day) if len(str(start_date.day)) == 1 else start_date.day}'

        end_day = last_day_of_month(year, month)
        end_date = f'{start_date.year}-{"0" + str(start_date.month) if len(str(start_date.month)) == 1 else start_date.month}-{"0" + str(end_day) if len(str(end_day)) == 1 else end_day}'

        return start_date_ret, end_date
    except Exception as ex_:
        print(f'ошибка функции {date_start_stop.__name__}  {ex_}')


def pred_month():
    """функция возвращает даты на начало и конец предыдущего месяца

    Returns:
        _type_: _description_
    """
    try:
        previous_month_date = datetime.now() + relativedelta(months=-1)
        first_date_pred_month = f'{previous_month_date.year}-{"0" + str(previous_month_date.month) if len(str(previous_month_date.month)) == 1 else previous_month_date.month}-{"01"}'
        last_day = last_day_of_month(previous_month_date.year, previous_month_date.month)
        last_date_pred_month = f'{previous_month_date.year}-{"0" + str(previous_month_date.month) if len(str(previous_month_date.month)) == 1 else previous_month_date.month}-{"0" + str(last_day) if len(str(last_day)) == 1 else last_day}'
        return first_date_pred_month, last_date_pred_month
    except Exception as ex_:
        print(f'ошибка функции {pred_month.__name__}  {ex_}')


def update_file(link: str, sleep_: int = 30):
    """обновление сводной таблицы Excel
    # блок импортов для обновления сводных
    import pythoncom
    pythoncom.CoInitializeEx(0)
    import win32com.client
    Args:
        link (_type_): ссылка на файл - который нужно обновить
        sleep_(int): задержка в сек на обновление сводной таблицы
    """
    try:
        xlapp = win32com.client.DispatchEx("Excel.Application")
        wb = xlapp.Workbooks.Open(link)
        wb.Application.AskToUpdateLinks = False  # разрешает автоматическое  обновление связей (файл - парметры - дополнительно - общие - убирает галку запрашивать об обновлениях связей)
        wb.Application.DisplayAlerts = True  # отображает панель обновления иногда из-за перекрестного открытия предлагает ручной выбор обновления True - показать панель
        wb.RefreshAll()
        # xlapp.CalculateUntilAsyncQueriesDone() # удержит программу и дождется завершения обновления. было прописано time.sleep(30)
        time.sleep(sleep_)  # задержка 60 секунд, чтоб уж точно обновились сводные wb.RefreshAll() - иначе будет ошибка
        wb.Application.AskToUpdateLinks = True  # запрещает автоматическое  обновление связей / то есть в настройках экселя (ставим галку обратно)
        wb.Save()
        wb.Close()
        xlapp.Quit()
        wb = None  # обнуляем сслыки переменных иначе процесс эксель не завершается и висит в дистпетчере
        xlapp = None  # обнуляем сслыки переменных иначе процесс эксел ь не завершается и висит в дистпетчере
        del wb  # удаляем сслыки переменных иначе процесс эксель не завершается и висит в дистпетчере
        del xlapp  # удаляем сслыки переменных иначе процесс эксель не завершается и висит в дистпетчере
    except Exception as ex_:
        print(f'ошибка функции {update_file.__name__} {ex_} не удалось обновить файл по ссылке {link}')


def send_mail(send_to: list,
              send_cc: list,
              send_bcc: list,
              topic_text: str,
              body_text: str,
              file_link: str,
              file_name: str,
              SEND_FROM: str,
              SERVER: str,
              PORT: int,
              USER_NAME: str,
              PASSWORD: str):
    """рассылка почты с вложением, пользователям в т.ч. добавление в копию и скрытую копию

    Args:
        send_to (list):  список адресов для рассылки
        send_cc (list):  список адресов для рассылки - копии (можно не заполнять - проставить пустой список)
        send_bcc (list): список адресов для рассылки - скриыте копии (можно не заполнять - проставить пустой список)

        topic_text(str): текст темы писма
        body_text(str):  текст тела писма

        file_link(str):  ссылка на файл
        file_name(str):  имя файла в данном варианте нужно указывать с расширением 'BAIC_MSK.xlsx' (имя должно быть на латинице иначе придет в кодировке bin)

        SEND_FROM (str):  email пользователя от кого будет отправлено сообщение
        SERVER (str):     имя сервера
        PORT (int):       порт
        USER_NAME (str):  имя пользователя в сети
        PASSWORD (str):   пароль пользователя (учетной записи в сети)

        Пример:
        send_mail(['skrqqqo@siml-auto.ru'],             # send_to
          [],                                           # send_cc
          ['krutkosergey11111@yandex.ru'],              # send_bcc
          f'Привет привет',                             # topic_text
          f'Здравствуйте \nВо вложении файлик',         # body_text
          "//local/data/BAIC_MSK.xlsx",                 # file_link
          'BAIC_MSK.xlsx',                              # file_name
          'skrqqqo@siml-auto.ru',                       # SEND_FROM
          'server-vm23.LOCAL',                          # SERVER
          555,                                          # PORT
          'skrut',                                      # USER_NAME
          'ZZZZZZZxxxxxx1111a')                         # PASSWORD

    """

    try:
        send_from = SEND_FROM
        subject = topic_text
        text = body_text
        files = fr'{file_link.strip()}'
        server = SERVER
        port = PORT
        username = USER_NAME
        password = PASSWORD
        isTls = True

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = ','.join(send_to)
        msg["Cc"] = ','.join(send_cc)
        msg["Bcc"] = ','.join(send_bcc)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(text))

        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(files, "rb").read())
        encoders.encode_base64(part)

        part.add_header('Content-Disposition',
                        f'attachment; filename={file_name.strip()}')  # имя файла должно быть на латинице иначе придет в кодировке bin
        msg.attach(part)

        smtp = smtplib.SMTP(server, port)
        if isTls:
            smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(send_from, send_to + send_cc + send_bcc, msg.as_string())
        smtp.quit()

    except Exception as ex_:
        print(f'ошибка функции {send_mail.__name__} {ex_} входне параметры {send_to} {file_link} {file_name}')

###############
def open_df_locked(link: str, password: str, lst_name=None):
    print('open_df_locked')
    """функция обработки заблокированных книг EXCEL с паролем

    Args:
        link (str): ссылка на книгу
        password (str): пароль
        lst_name (str): название листа можно ввести и откроет конкретный лист, если нет то по умолчанию

    Returns:
        _type_ (df, list): вовзращает df и список листов в книге
    """
    try:
        lnk = link
        passwd = password  # пароль книги excel
        decrypted_workbook = io.BytesIO()
        with open(lnk, 'rb') as file:
            office_file = msoffcrypto.OfficeFile(file)
            office_file.load_key(password=passwd)
            office_file.decrypt(decrypted_workbook)

        xlsx_file = pd.ExcelFile(decrypted_workbook)
        sheet_names = xlsx_file.sheet_names  # получаем имена листов в книге
        if lst_name == None:
            df = pd.read_excel(decrypted_workbook)
            return df, sheet_names
        else:
            df = pd.read_excel(decrypted_workbook, sheet_name=lst_name)
            return df, sheet_names
    except Exception as ex_:
        print(f"{open_df_locked.__name__} - ОШИБКА", {ex_})


def open_df_unlocked(link: str, lst_name=None):
    print('open_df_unlocked')
    """функция обработки не заблокированный книг EXCEL без пароля

    Args:
        link (str): ссылка на книгу
        lst_name (str): название листа можно ввести и откроет конкретный лист, если нет то по умолчанию

    Returns:
        _type_ (df, list): вовзращает df и список листов в книге
    """
    try:
        lnk = link
        if lst_name == None:
            df = pd.read_excel(lnk, dtype='str')
            sheet_names = list(pd.read_excel(lnk, sheet_name=None).keys())
            return df, sheet_names
        else:
            df = pd.read_excel(lnk, sheet_name=lst_name, dtype='str')
            sheet_names = list(pd.read_excel(lnk, sheet_name=None).keys())
            return df, sheet_names

    except Exception as ex_:
        print(f"{open_df_unlocked.__name__} - ОШИБКА", {ex_})


def open_dataframe(link, password='0', lst_name=None):
    print('open_dataframe')
    """функция открытия книги с паролем или без (задействует две доп функции)

    Args:
        link (_type_): ссылка на книгу
        password (str, optional): пароль. Defaults to '0'.
        lst_name (_type_, optional): Имя листа. Defaults to None.

    Returns:
        _type_: _description_
    """
    try:
        if len(password) > 1:
            df, sheet_names = open_df_locked(link, password, lst_name)
            return df, sheet_names
        else:
            df, sheet_names = open_df_unlocked(link, lst_name)
            return df, sheet_names
    except Exception as ex_:
        print(f"{open_dataframe.__name__} - ОШИБКА", {ex_})


def tek_day(format:str = 'dt' or 'str'):
    """
    функция возращает дату на сегодня в datetime или str (по умолчанию datetime)
    :param format: str указать тип 'dt' or 'str' дата вернется в типе datetime или str
    :return:
    """
    try:
        import datetime
        if format=='dt': return datetime.date.today()
        elif format=='str': return datetime.date.today().isoformat()
        else: return f'Выберете возdращаемый формат даты: dt or str'
    except Exception as ex_:
        print(f'ошибка {ex_} функция - {tek_day.__name__}')


def all_letters():
    'все буквы ru_eng алфавита'

    import string
    try:
        eng = string.ascii_letters
        ru = ''.join(map(chr, range(ord('А'), ord('я') + 1))) + 'Ёё'
        res = eng + ru
        return res
    except Exception as ex_:
        print(f'ошибка {ex_} функция - {all_letters.__name__}')


def read_datafarme(link):
    """считывает ссылку на книгу и получает имена всех листов и датафреймы
    переводит все имена листов в верхний регистр

    Args:
        link (_type_): сслыка на файл !!! ВАЖНО перед ссылкой fr

    Returns:
        получаем все датафреймы и имена листов
    """
    try:
        df_ = pd.read_excel(link, sheet_name=None)
        df_ = {key.upper(): value for key, value in df_.items()}  # привели названия листов в единый регистр
        df_names_lists = df_.keys()                               # получили все названия листов книги
        return df_, df_names_lists
    except Exception as ex_:
        print(f'ошибка {ex_} функция - {read_datafarme.__name__}')

def list_date_work(YEAR=2025, MONTH=8, DAY=4, correct_last_day = 0):
    """функция формируюящая список дат с и по сегодня (последнюю дату можно корректировать +.-)
    даты возвращаются в формате datetime
    """
    import datetime
    try:
        start_date = datetime.datetime(YEAR, MONTH, DAY) # начальная дата
        cur = (datetime.date.today()-timedelta(days=correct_last_day)).strftime('%Y-%m-%d').split('-') # текущая дата минус 1 день
        end_date = datetime.datetime(int(cur[0]), int(cur[1]), int(cur[-1]))             # текущая дата минус 1 день

        res = pd.date_range(
            min(start_date, end_date),
            max(start_date, end_date)
        ).tolist() #.strftime('%d/%m/%Y').tolist()
        return res
    except Exception as ex_:
        print(f'ошибка {ex_} функция - {list_date_work.__name__}')


def shapka(table, text_head='VIN', cordinat_x = 20, cordinat_y = 20):
    """ функция ищет в какой строке находится шапка таблицы, путём поиска "VIN" в ограниченной таблице table.iloc[0:20,0:20] клеток
                    и вырезает лишние куски до найденной шапки и вместе с ней
                    если ошибка, то оставляем входную таблицу оставляем без именений

    Args:
        table (_type_): таблица
        text_head (str, optional): поиск по ключевому слову в шапке. Defaults to 'VIN'.

    Returns:
        table: таблица только с заголовками без верхних вспомогательных строк
    """

    try:
        table = table.T.reset_index().T.reset_index(drop=True)  # опускает имена столбцов в первую строку
        qqq = table.iloc[0:cordinat_x, 0:cordinat_y]  # кординаты поиска
        # находим в какой строке находится шапка таблицы
        qqq = qqq[qqq.astype(str).apply(lambda x: x.astype(str).str.upper().str.contains(text_head, case=False)).any(axis=1)]
        q = qqq.index[0]
        table.columns = table.loc[q]
        table = table.iloc[q + 1:, :]
        table = table.reset_index(drop=True)
        table = table[table.columns.dropna()]
        return table
    except:
        return table


def poisk_shapki_df(df, text_head='vin'):
    """первичная обработка df
    находит шапку таблицы по значению VIN в строках и делает эту строку заголовком таблицы

    Args:
        df (_type_): подаем df

    Returns:
        _type_: возращает df
    """
    try:
        count_col = 0
        for i in df.columns:
            if str(i).lower() == 'vin':
                count_col += 1
            counter_vin = df[i].apply(lambda x: str(x).lower()).str.contains(
                f'^{text_head}').sum()  # ^ - в регулярке используется для поиска когда слово начинается с
            name_column = i
            row_number = None

            if counter_vin > 0:
                row_number = df[df[name_column].apply(lambda x: str(x).lower()) == f'{text_head}'].index[0]
                # print(f"VIN найден в столбце {i}")
                break

        if count_col != 0:
            return df  # если шапка в первой строке, ничего не изменяем
        else:
            new_header = df.iloc[row_number]  # берем первую строку как заголовок
            df = df[row_number + 1:]  # отбрасываем исходный заголовок
            df.rename(columns=new_header, inplace=True)  # переименовываем столбцы
            return df
    except Exception as ex_:
        print(f'{poisk_shapki_df.__name__} ошибка {ex_} не удалось записать данные в файл')


def convert_bad_dates_in_columns(df, name_df_col: str, format='mixed'):
    """функция для преобразования кривых формат дат, в том числле формата 41253
    Подается df и имя столбца
    format='ISO8601' or format='mixed'
    Args:
        df (dataframe):
        name_date_columns (str): имя столбца с датой (который хотим преобразовать).
        format (str) : указывается формат 'ISO8601' or format='mixed' по умолчанию 'mixed'.
    Returns:
        _type_: возварщает преобразованный df
    """
    try:
        from datetime import datetime

        formating = (lambda x: datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(x) - 2))
        df[name_df_col] = df[name_df_col].apply(
            lambda x: str(x).replace('00:00:00', '').strip() if '00:00:00' in str(x) else x)
        df[name_df_col] = df[name_df_col].apply(lambda x: formating(x) if len(str(x)) == 5 and str(x)[0] == '4' else x)
        df[name_df_col] = pd.to_datetime(df[name_df_col], format=format, errors='ignore')
        return df
    except Exception as ex_:
        print(f"{convert_bad_dates_in_columns.__name__} - ОШИБКА", {ex_})


def convert_col_to_float(df, name_colums: list = [None], error_ = "ignore"):
    """конвертирует нужные (указанные) столбцы df в float

    Args:
        df (_type_): df для обработки
        name_colums (list, optional): имя/имена столбцов которое будем искать в df
        error (str): Expected type 'Literal["ignore", "raise", "coerce"]'
    Returns:
        _type_: _description_
    """
    try:
        for i in name_colums:
            for j in df.columns:
                if i in j:
                    df[j] = pd.to_numeric(df[j], errors = error_)

        return df
    except Exception as ex_:
        print(f'ошибка {ex_} функция - {convert_col_to_float.__name__} запнулось на {i, j}')
        print(f'Возможно не указаны имена столбцов для поиска в df')

def convert_col_to_int(df, columns:list, fillna_=True, error_='ignore'):
    """преобразует чиловые значения в один формат int
    NA = 0
    Args:
        df (_type_): dataframe
        columns (list): список столбцов которые преобразовываем
        fillna_ (bool): True or False
    Returns:
        _type_: _description_
    """
    try:
        for i in columns:
            df[i] = df[i].astype('float', errors=error_)
            df[i] = df[i].astype('int', errors=error_)
            if fillna_:
                df[i] = df[i].fillna(0)
            df[i] = df[i].astype('int')
        return df
    except Exception as ex_:
        print(f"{convert_col_to_int.__name__} - ОШИБКА", {ex_})




