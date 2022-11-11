# --------------------------------------------------------------------------------------------------------------------
# нужно сделать запросы:
# -вывести все оценки по предмету, оценки группы -------------------------------------------------------------- ГОТОВО
# -вывести то же самое для зачётов ---------------------------------------------------------------------------- ГОТОВО
# -вывести список группы -------------------------------------------------------------------------------------- ГОТОВО
# -вывести список потока
# -добавить студента в базу, исключить студента из базы
# -добавить предмет в базу, исключить предмет из базы
# -изменить оценку студента
# ДОПОЛНИТЕЛЬНО: сделать единый шаблон запроса для зачётов, экзаменов и списка группы,
# ДОПОЛНТИЕЛЬНО: оценки конкретных студетов по шифру
# а в функции менять только нужные поля
# --------------------------------------------------------------------------------------------------------------------

from elasticsearch import Elasticsearch
import json

ADDRESS_LOCAL = ["http://localhost:9200"]  # адрес БД на локальной машине
# ADDRESS_REMOTE = ["http://172.26.62.178:9200"]  # адрес БД на сторонней машине

es = Elasticsearch(hosts=ADDRESS_LOCAL)

# ВАЖНО!!! В БАЗЕ ТЕПЕРЬ НЕ НУЖНО ПРОПИСЫВАТЬ QUERYконкретные оценки по предмету, все оценки по предмету,


def mark_query(group_name, subject_sipher, marks_to_print, all_groups_flag=False):  # запрос на экзамены или зачёты
    # с конкретными оценками(оценкой)
    fields = ['student name', 'surname', 'father name', 'group', 'subject name', 'date']
    body = {"bool": {
        "must": [
            {"terms": {"mark": marks_to_print}},  # требуемые оценки
            {"match": {"group.keyword": group_name}},  # номер группы, keyword здесь задаёт жёсткий поиск
            {"match": {"subject sipher": subject_sipher}}  # шифр предмета
        ]
    }
    }
    if all_groups_flag:  # если нужно вывести все группы, удаляем поле "группа"
        body['bool']['must'].pop(1)

    res = es.search(index="database", query=body, size=100, from_=0, source=fields)['hits']['hits']
    ret = []
    for i in res:
        ret.append(i['_source'])
    return ret


def group_list_query(group_name, all_groups_flag=False):  # возвращает список группы или потока
    fields = ['student name', 'surname', 'father name', 'group', 'student cipher']
    body = {"bool": {
        "must": [
            {"match": {"group.keyword": group_name}}]
        }
    }
    if all_groups_flag:  # если нужно вывести все группы, удаляем поле "группа"
        body['bool']['must'].pop(0)
        f1 = {"match": {"group": group_name[:4]}}  # если нудно вывести весь поток, в запрос добавляется название
        f2 = {"match": {"group": group_name[-2:]}}  # направления и год начала обучения
        body['bool']['must'].append(f1)
        body['bool']['must'].append(f2)
    res = es.search(index="database", query=body, size=1000, from_=0, source=fields)['hits']['hits']
    ret = []
    for i in res:
        j = i['_source']
        if j not in ret:
            ret.append(i['_source'])
    return ret


def remove_student(student_cipher):
    body = {
        "from": 0,
        "size": 6,
        "query": {
            "bool": {
                "must": {"match": {"student cipher": student_cipher}}
            }
        }
    }
    res_students = es.search(index="students", body=body)  # поиск данных студента во всех индексах
    # res_students = es.search(index="students", query=body['query'], size=body['size'], from_=0)
    res_exams = es.search(index="exams", body=body)
    res_zachet = es.search(index="zachet", body=body)

    reserve = open('reserve.txt', 'w')  # создание копии на всякий случай
    reserve.write('STUDENT' + '\n' + str(res_students['hits']['hits'][0]['_source']) + '\n'
                  + str(res_exams['hits']['hits'][0]['_source']) + '\n'
                  + str(res_zachet['hits']['hits'][0]['_source']) + '\n\n')

    id_students = res_students['hits']['hits'][0]['_id']  # выделение id в отдельном блоке для читаемости
    id_exams = res_exams['hits']['hits'][0]['_id']
    id_zachet = res_zachet['hits']['hits'][0]['_id']

    reserve.close()
    '''es.delete(index="students", id=id_students)  # удаление студента из всех индексов
    es.delete(index="exams", id=id_exams)
    es.delete(index="zachet", id=id_zachet)'''
    # РАСКОММЕНТИРОВАТЬ КОГДА ПЕРЕПИШУ ПРИСВОЕНИЕ ШИФРА СТУДЕНТАМ


def add_student(student_cipher, name, surname, father_name, course, group):
    body = {'student cipher': student_cipher,
            'name': name,
            'surname': surname,
            'father name': father_name,
            'course': course,
            'group': group
            }
    es.index(index='students', body=body)


def remove_subject(subject_cipher, exam_flag):  # если флаг равен 1, это экзамен. Если 0, это зачёт
    body = {
        "from": 0,
        "size": 6,
        "query": {
            "bool": {
                "must": {"match": {"subject cipher": subject_cipher}}
            }
        }
    }

    reserve = open('reserve.txt', 'w')  # создание копии на всякий случай
    if exam_flag == 1:
        res_exams = es.search(index="exams", body=body)
        reserve.write('-' * 10 + 'EXAM' + '-' * 10 + '\n' + str(res_exams['hits']['hits'][0]['_source']) + '\n\n')
        id_exams = res_exams['hits']['hits'][0]['_id']
        # es.delete(index="exams", id=id_exams)
        # РАСКОММЕНТИРОВАТЬ КОГДА ПЕРЕПИШУ ПРИСВОЕНИЕ ШИФРА СТУДЕНТАМ

    else:
        res_zachet = es.search(index="zachet", body=body)
        reserve.write('-' * 10 + 'ZACHET' + '-' * 10 + '\n' + str(res_zachet['hits']['hits'][0]['_source']) + '\n\n')
        id_zachet = res_zachet['hits']['hits'][0]['_id']
        # es.delete(index="zachet", id=id_zachet)
        # РАСКОММЕНТИРОВАТЬ КОГДА ПЕРЕПИШУ ПРИСВОЕНИЕ ШИФРА СТУДЕНТАМ
    reserve.close()


def add_subject():
    pass


if __name__ == '__main__':
    #a = mark_query("КРМО-01-22", "2000", [3])
    a = group_list_query("КРМО-01-22", True)
    from pprint import *

    pprint(a)
    print(len(a))
    # remove_student(1002)
    '''res = group_list_query(3)
    for i in range(len(res["hits"]["hits"])):
        print(i, ": ", res["hits"]["hits"][i]["_source"])'''
