# ---------------------------------------------------------------------------------------------------------------------
# ЭТОТ ФАЙЛ СОЗДАЕТ БАЗУ ДАННЫХ И ЗАПОЛНЯЕТ ЕЁ ДАННЫМИ, СГЕНЕРИРОВАННЫМИ В ФАЙЛЕ studentGen
# ИСПОЛНЯЕТСЯ 1 РАЗ. ЕСЛИ ИСПОЛНИТЬ ПОВТОРНО, СГЕНЕРИРУЮТСЯ НОВЫЕ СПИСКИ СТУДЕНТОВ И ДОБАВЯТСЯ К СУЩЕСТВУЮЩИМ
# ---------------------------------------------------------------------------------------------------------------------

from elasticsearch import Elasticsearch
import studentGen

es = Elasticsearch(hosts=["http://localhost:9200"])
# print(es.ping())

studentGen.generate(studentGen.group1_1, 1, 'КРМО-01-22')  # генерирует список групп, оценки за экзамен, зачёты
studentGen.generate(studentGen.group1_2, 1, 'КРМО-02-22')
studentGen.generate(studentGen.group2_1, 2, 'КРМО-01-21')
studentGen.generate(studentGen.group2_2, 2, 'КРМО-02-21')

es.indices.create(index="students")  # 4 индекса для студентов, экзаменов, зачётов и дисциплин
es.indices.create(index="exams")
es.indices.create(index="zachet")
es.indices.create(index="diciplines")

for i in studentGen.group1_1:  # заполнение списков групп
    res = es.index(index='students', body=i)
    print(res)

for i in studentGen.group1_2:
    res = es.index(index='students', body=i)
    print(res)

for i in studentGen.group2_1:
    res = es.index(index='students', body=i)
    print(res)

for i in studentGen.group2_2:
    res = es.index(index='students', body=i)
    print(res)


for i in studentGen.zachet:  # заполнение зачётов, экзаменов, дисциплин
    res = es.index(index='zachet', body=i)
    print(res)

for i in studentGen.exams:
    res = es.index(index='exams', body=i)
    print(res)

for i in studentGen.diciplines:
    res = es.index(index='diciplines', body=i)
    print(res)
