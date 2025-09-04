# Набор некоторых функций которые будут становиться лучше

### Модули которые могут потребоваться (устанавливаются по умолчанию)
    import pandas, pywin32, openpyxl, msoffcrypto-tool

### Импорт функций после установки

    import magnuslib.main as mg
    # или
    from magnuslib import main as mg

## links_main()
Функция: для работы с путями, ссылки, вводные данные хранятся в блокноте
имеют 2 поля (пример текстового блокнота ниже):

ключ;значение       
server;local/32/rut     
pass;111

вызов функции `links_main('ключ', 'значение', 'f_links.txt', 'server', sep=';')` **return** `111`

    
    links_main(name_column_key, name_column_result, name_file, key, sep=';')

## dir_link()
Функция : возвращает полный путь к директории
работает в `.py .ipynb` **return**
`C:\Users\sergey_krutko\PycharmProjects\magnuslb\magnuslib`

    dir_link()

## yesterday()
Функция : возвращает дату на вчера - по уморлчанию минус 1 день, можно регулировать +.-
**result** `2025-08-04 00:01:51.921337` format `datetime`

    yesterday() # или yesterday(5)

## create_date()
Функция : создает дату в формате `datetime`     
`create_date(2025, 12, 12)` return `2025-12-12`

    create_date()

## converter_month_to_int()
Функция : конвертирует месяц в число            
`converter_month_to_int('май')` return `5`

    converter_month_to_int()

## last_day_of_month()
Функция : возвращает последний день указанного месяца и года        
`last_day_of_month(2025, 5)` return `31`

    last_day_of_month()    

## date_start_stop()
Функция : возвращает начало и конец периода в формате YYYY-MM-DD       
`date_start_stop(2025, 7)` return `('2025-07-01', '2025-07-31')`

    date_start_stop() 

## update_file()
Функция : бновление сводной таблицы Excel      
`update_file('myFile.xlsx')` return `update sv.tabl in file 'myFile.xlsx'`

    update_file() 

## send_mail()
Функция : рассылки почты
```
send_mail(['skrqqqo@siml-auto.ru'],                     # send_to
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
   ```


## open_dataframe()
Функция : открытие файла Excel с паролем и без
`print(open_dataframe(fr'\\Mac\Home\Desktop\Лист Microsoft Excel.xlsx','1111'))`

    open_dataframe()

## tek_day()
Функция : возращает дату на сегодня в datetime или str (по умолчанию datetime)

`tek_day()` return `2025-08-06`

    tek_day()

## all_letters()
Функция : возращает все буквы `ru_eng` алфавита

`all_letters()` return `abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяЁё`

## convert_col_to_float()
Функция : конвертирует нужные (указанные) столбцы df в float    
`convert_col_to_float(df, name_colums: list = ['внесено_в_рублях', 'цена'])`

    convert_col_to_float()    

## convert_col_to_int()
Функция : конвертирует нужные (указанные) столбцы df в int
`convert_col_to_int(df, name_colums: list = ['внесено_в_рублях', 'цена'])`

    convert_col_to_int

## read_datafarme()
Функция : читывает ссылку на книгу и получает имена всех листов и датафреймы
    переводит все имена листов в верхний регистр

    read_datafarme()

## list_date_work()
Функция : функция формируюящая список дат с и по сегодня (последнюю дату можно корректировать +.-)
`list_date_work(YEAR=2025, MONTH=8, DAY=4, correct_last_day = 0)` return `[Timestamp('2025-08-04 00:00:00'), Timestamp('2025-08-05 00:00:00'), Timestamp('2025-08-06 00:00:00')]`

    list_date_work()

## shapka()
Функция : функция ищет в какой строке находится шапка таблицы, путём поиска "VIN" в ограниченной таблице `table.iloc[0:20,0:20]` клеток (параметры меняются)
и вырезает лишние куски до найденной шапки и вместе с ней если ошибка, то оставляем входную таблицу оставляем без именений
`shapka(table, text='VIN', cordinat_x = 20, cordinat_y = 20)`

    shapka()

## poisk_shapki_df()
Функция : функция ищет в какой строке находится шапка таблицы, путём поиска "VIN"
`poisk_shapki_df(df, text_head="vin")`

    poisk_shapki_df()

## convert_bad_dates_in_columns()
Функция : преобразования кривых формат дат, в том числле формата 41253
`convert_bad_dates_in_columns(df, name_df_col: str, format='mixed')`

    convert_bad_dates_in_columns()


    



    
