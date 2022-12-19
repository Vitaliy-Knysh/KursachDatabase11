# --------------------------------------------------------------------------------------------------------------------
# нужно сделать запросы:
# -вывести все оценки по предмету, оценки группы -------------------------------------------------------------- ГОТОВО
# -вывести то же самое для зачётов ---------------------------------------------------------------------------- ГОТОВО
# -вывести список группы -------------------------------------------------------------------------------------- ГОТОВО
# -вывести список потока -------------------------------------------------------------------------------------- ГОТОВО
# -добавить студента в базу, исключить студента из базы ------------------------------------------------------- ГОТОВО
# -добавить предмет в базу, исключить предмет из базы --------------------------------------------------------- ГОТОВО
# -изменить оценку студента ----------------------------------------------------------------------------------- ГОТОВО
# --------------------------------------------------------------------------------------------------------------------

from elasticsearch import Elasticsearch
from pprint import *
import os

import json

ADDRESS_LOCAL = ["http://localhost:9200"]  # адрес БД на локальной машине
ADDRESS_REMOTE = ["http://172.26.62.178:9200"]  # адрес БД на сторонней машине

es = Elasticsearch(hosts=ADDRESS_LOCAL)


def mark_query(group_name, subject_cipher, marks_to_print, all_groups_flag=False):
    """запрос на экзамены или зачёты с конкретными оценками(оценкой)"""

    fields = ['student name', 'surname', 'father name', 'group', 'subject name', 'date']
    body = {"bool": {
        "must": [
            {"terms": {"mark": marks_to_print}},  # требуемые оценки
            {"match": {"group.keyword": group_name}},  # номер группы, keyword здесь задаёт жёсткий поиск
            {"match": {"subject cipher": subject_cipher}}  # шифр предмета
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


def group_list_query(group_name, all_groups_flag=False):
    """возвращает список группы или потока"""

    fields = ['student name', 'surname', 'father name', 'group', 'student cipher', 'course']
    body = {"bool": {
        "must": [
            {"match": {"group.keyword": group_name}}]
        }
    }
    if all_groups_flag:  # если нужно вывести весть поток
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
    """удаляет студента из базы данных, создает резервную копию"""

    body = {
            "bool": {
                "must": {"match": {"student cipher": student_cipher}}
            }
        }
    res = es.search(index="database", query=body, size=15, from_=0)
    copy_counter = 0
    dir_name = str('reserve_students/' + res['hits']['hits'][0]['_source']['surname'] + '_' +
                   res['hits']['hits'][0]['_source']['student name'] + '_' + res['hits']['hits'][0]['_source']['group'])
    os.mkdir(dir_name)
    for doc in res['hits']['hits']:  # создание резервной копии документа в json формате
        with open((dir_name + '/' + str(copy_counter) + '.json'), 'w+') as f:
            json.dump(doc['_source'], f, ensure_ascii=False)
        copy_counter += 1
        es.delete(index="students", id=doc['_id'])
        pprint(dict(res))


def add_student(student_cipher, name, surname, father_name, course, group_name):
    """добавляет студента в базу данных"""

    fields = ['subject name', 'date', 'hours', 'subject cipher', 'student cipher']
    body = {"bool": {
        "must": {"match": {"group.keyword": group_name}},
    }
    }
    res = es.search(index="database", query=body, size=15, from_=0, source=fields)['hits']['hits']
    diciplines = []
    for i in res:  # из получнных документов нужно получить список дисциплин без повторений.
        if i['_source']['student cipher'] == res[0]['_source']['student cipher']:  # больше 15 их точно не будет
            diciplines.append(i['_source'])

    for dicipline in diciplines:  # создание списка не сданных дисциплин для нового студента
        body = {'student cipher': student_cipher,
                'name': name,
                'surname': surname,
                'father name': father_name,
                'course': course,
                'group': group_name,
                'date': dicipline['date'],
                'hours': dicipline['hours'],
                'subject cipher': dicipline['subject cipher'],
                'subject name': dicipline['subject name'],
                'mark': 'Не сдано'
                }
        es.index(index='students', body=body)
        pprint(body)
        es.update


def remove_subject(subject_cipher):
    """удаляет предмет из базы данных, создаёт резервную копию"""

    body = {
        "bool": {
            "must": {"match": {"subject cipher": subject_cipher}}
        }
    }
    res = es.search(index="database", query=body, size=1000, from_=0)
    dir_name = str('reserve_subjects/' + res['hits']['hits'][0]['_source']['subject name'])
    os.mkdir(dir_name)
    for doc in res['hits']['hits']:  # создание резервной копии документа в json формате
        with open((dir_name + '/' + doc['_source']['surname'] + '_' + doc['_source']['student name'] + '_' +
                   doc['_source']['group'] + '.json'), 'w+') as f:
            json.dump(doc['_source'], f, ensure_ascii=False)
        es.delete(index="database", id=doc['_id'])


def add_subject(subject_name, subject_cipher, date, hours, base_group):
    """добавляет предмет в базу данных"""

    students = group_list_query(base_group, True)
    for student in students:  # создание списка не сданных дисциплин для нового студента
        body = {'student cipher': student['student cipher'],
                'name': student['student name'],
                'surname': student['surname'],
                'father name': student['father name'],
                'course': student['course'],
                'group': student['group'],
                'date': date,
                'hours': hours,
                'subject cipher': subject_cipher,
                'subject name': subject_name,
                'mark': 'Не сдано'
                }
        es.index(index='students', body=body)
        pprint(body)


def change_student_mark(student_cipher, subject_cipher, mark):
    """изменяет оценку студента"""

    body = {
        "bool": {
            "must": [{"match": {"student cipher": student_cipher}},
                     {"match": {"subject cipher": subject_cipher}}]
        }
    }
    res = es.search(index="database", query=body, size=1, from_=0, source=['_id'])['hits']['hits']
    body = {'doc': {'mark': mark}}
    es.update(index='database', id=res[0]['_id'], body=body)


def restore_student(student_name, student_surname, group):
    """восстановление студента из резервной копии"""

    dir_name = 'reserve_students/' + student_name + '_' + student_surname + '_' + group
    files = os.listdir(dir_name)
    for file in files:
        with open(dir_name + '/' + file) as f:
            card = json.load(f)
            es.index(index="database", body=card)
            pprint(card)


def restore_subject(subject_name):
    """восстановление предмета из резервной копии"""

    dir_name = 'reserve_subjects/' + subject_name
    files = os.listdir(dir_name)
    for file in files:
        with open(dir_name + '/' + file) as f:
            card = json.load(f)
            es.index(index="database", body=card)
            pprint(card)

def get_display_data():
    """возвращает названия и щифры всех предметов, все группы студентов"""

    subject_list = []
    group_name_list = []
    source = ['subject name', 'subject cipher', 'group']
    body = {
        "bool": {
            "must": {"match_all": {}},
        }
    }
    res = es.search(index="database", query=body, size=10000, source=source)['hits']['hits']
    for doc in res:
        string_to_add = str(doc['_source']['subject cipher']) + ' - ' + str(doc['_source']['subject name'])
        if string_to_add not in subject_list:
            subject_list.append(string_to_add)
        if doc['_source']['group'] not in group_name_list:
            group_name_list.append(doc['_source']['group'])
    return subject_list, group_name_list

# a, b = get_display_data()
# pprint(b)
