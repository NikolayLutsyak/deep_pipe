 1. Конфиг
 - Конфиг это текстовый файл
 2. Датасет
 - Датасеты бывают полностью кэширующими и полностью не кэширующими. 
 - Нужно ли использовать кэширующий датасет определено в конфиге.
 - Датасеты, описанные пользователями изначально не кэширующие, но есть класс, делающий любой инициализированный датасет кэширующим.
 - Некоторые датасеты имеют разный пространственный рамер для сканов
 3. Батч итераторы
 - Существуют батч итераторы, которые хотят именно некэширующий датасет
 - Батч итераторы создаются на каждой эпохе
 - Батч итераторы просят или датасет и идентификаторы пациентов или готовые данные
 4. Сплит и скрипт
 - Сплит и скрипт определяют парадигму эксперимента
 - Задача скрипта - корректная обработка выхода сплиттера, описание иерархия логов 
 - Каждый сплиттер возвращает набор наборов ... наборов идентификаторов пациентов
 - Результат сплиттера детерминирован входом, не рандомен
 
 
 - Существует функция подгрузки данных по идентификаторам