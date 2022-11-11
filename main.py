# --------------------------------------------------------------------------------------------------------------------
# нужно сделать запросы:
# -вывести конкретные оценки по предмету, все оценки по предмету, оценки группы
# -вывести то же самое для зачётов
# -вывести список группы
# -добавить студента в базу, исключить студента из базы
# -добавить предмет в базу, исключить предмет из базы
# -изменить оценку студента
# ДОПОЛНИТЕЛЬНО: сделать единый шаблон запроса для зачётов, экзаменов и списка группы,
# а в функции менять только нужные поля
# --------------------------------------------------------------------------------------------------------------------

from elasticsearch import Elasticsearch
import json

ADDRESS_LOCAL = ["http://localhost:9200"]  # адрес БД на локальной машине
#ADDRESS_REMOTE = ["http://172.26.62.178:9200"]  # адрес БД на сторонней машине

es = Elasticsearch(hosts=ADDRESS_LOCAL)

# ВАЖНО!!! В БАЗЕ ТЕПЕРЬ НЕ НУЖНО ПРОПИСЫВАТЬ QUERY

def mark_query(group_name, subject_sipher, marks_to_print):  # запрос на список студентов одной группы
                                                             # с конкретными оценками(оценкой)
    body = {"bool": {
                "must": [
                    #{"terms": {"mark": marks_to_print}},  # требуемые оценки
                    {"match": {"group": group_name}},  # номер группы
                    #{"match": {'2000'}}  # шифр предмета
                    ]
                }
    }
    unfiltered_data = es.search(index="database", query=body, size=100, from_=0)
    return unfiltered_data['hits']['hits']


def zachet_query(group_number, subject_sipher, marks_to_print):
    gte = 1000 + ((group_number - 1) * 20)  # с этого числа начинается отсчёт студентов группы
    lte = 999 + (group_number * 20)  # с этого числа заканчивается отсчёт студентов группы
    body = {
        "from": 0,
        "size": 20,
        "query": {
            "bool": {
                "must": [
                    {"terms": {"mark": marks_to_print}},  # требуемые оценки
                    {"match": {"subject cipher": subject_sipher}},  # шифр предмета
                    {"range": {"student cipher": {"gte": gte, "lte": lte}}}  # шифр студентов конкретной группы
                ]
            }
        }
    }
    return es.search(index="zachet", body=body)


def group_list_query(group_number):
    gte = 1000 + ((group_number - 1) * 20)  # с этого числа начинается отсчёт студентов группы
    lte = 999 + (group_number * 20)  # с этого числа заканчивается отсчёт студентов группы
    body = {
        "from": 0,
        "size": 20,
        "query": {
            "bool": {
                "must": [
                    {"range": {"student cipher": {"gte": gte, "lte": lte}}}  # шифр студентов конкретной группы
                ]
            }
        }
    }
    return es.search(index="students", body=body)


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
        #es.delete(index="exams", id=id_exams)
        # РАСКОММЕНТИРОВАТЬ КОГДА ПЕРЕПИШУ ПРИСВОЕНИЕ ШИФРА СТУДЕНТАМ

    else:
        res_zachet = es.search(index="zachet", body=body)
        reserve.write('-' * 10 + 'ZACHET' + '-' * 10 + '\n' + str(res_zachet['hits']['hits'][0]['_source']) + '\n\n')
        id_zachet = res_zachet['hits']['hits'][0]['_id']
        #es.delete(index="zachet", id=id_zachet)
        # РАСКОММЕНТИРОВАТЬ КОГДА ПЕРЕПИШУ ПРИСВОЕНИЕ ШИФРА СТУДЕНТАМ
    reserve.close()

def add_subject():
    pass


if __name__ == '__main__':
    a = mark_query('КРМО-01-22', '2000', [2, 3, 4, 5])
    import pprint
    pprint.pprint(a)
    #remove_student(1002)
    '''res = group_list_query(3)
    for i in range(len(res["hits"]["hits"])):
        print(i, ": ", res["hits"]["hits"][i]["_source"])'''
