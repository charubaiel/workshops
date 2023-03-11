# Arrow Ecosystem

1) Arrow - экосистема вокруг флексерного типа, ускоряющего и улучшающего все на свете

Имеем продвинутую среду продуктов, которые организуеются вокруг реализации дата типов на базе arrow
Массивы в Arrow — это наборы данных единого типа.
Это позволяет Arrow использовать наиболее эффективную реализацию для хранения данных и выполнения с ними вычислений.
Таким образом, каждый массив должен иметь данные и тип

2) Основной формат данных - колоночный parquet
    + фишки - колоночное решени, а значит синоним скорости
    + Умеет в сплитовани, так что можно в теории распределнно хранить
    + Умеет в комплексные функции за пределами базовых int,str,float
    + имеет схему данных, что в теории делает более прозрачную работу с форматом
    + Очень хорошо и эффективно шакалиться до маленьких размеров
    + Умеет в индексирование и партиционирование как большие братья бд
3) Основне новые либы:
    + Polars : Что то среднее между пандасом и спарком
        + Написан на расте , внутри себя оперирует стрелами
        + Умеет с ходу в параллельные вычисления и какую то там оптимизацию
        + Умеет в lazy загрузку и исполнение, что позволяет чуть более просто работать с большими данными
        + Обычно почти на порядок превосходит пандас операциях джоинов/групбаев/фильтров (Особенно с вери биг датой заметно)
    + DuckDB : аналог sqlite3 только в колоночном формате
        + Представляет из себя скоростной интерфейс SQL для над данными
        + Мало того что может работать как маленькая бдшка, так и умеет в inmemory вычисления
        + Умеет читать переменные прямо из питона, так что можо использовать ради конкретных функций или реализаций
            + Представим что у нас есть DataFrame в переменной df
            + Можем с ходу делать так new_df = conn.query('select * from df where will_use_clf == True')
            + Можно использовать например join / jaccard / window без необходимости переходить полностью на либу
        + Через `temp table` умеет очень удобно работать с данными без насирания на диск всяких дампов
        + Умеет в собирание файлов + http, то есть в теории можно указывать на пачку паркетников и работать с ними как с единым файлом
