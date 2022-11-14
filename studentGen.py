# ---------------------------------------------------------------------------------------------------------------------
# ЭТОТ ФАЙЛ СОЗДАЕТ СПИСОК СТУДЕНТОВ: 2 КУРСА ПО 2 ГРУППЫ, ОЦЕНКИ ЗА ЗАЧЁТ И ЭКЗАМЕН И ЗАПИСЫВАЕТ ИХ В БАЗУ ДАННЫХ.
# ИСПОЛНЯЕТСЯ ОДИН РАЗ
# ---------------------------------------------------------------------------------------------------------------------
import random
from pprint import *
from elasticsearch import Elasticsearch

ADDRESS_LOCAL = ["http://localhost:9200"]  # адрес БД на локальной машине
ADDRESS_REMOTE = ["http://172.26.62.178:9200"]  # адрес БД на сторонней машине

es = Elasticsearch(hosts=ADDRESS_LOCAL)

student_male_name = ["Иван", "Олег", "Василий", "Евгений", "Константин", "Виктор", "Александр", "Антон", "Игорь",
                     "Дмитрий", "Владислав", "Даниил", "Михаил", "Арсений"]
student_female_name = ["Алина", "Арина", "Анастасия", "Валентина", "Валерия", "Дарья", "Елена", "Екатерина",
                       "Елизавета", "Ирина", "Любовь", "Маргарита", "Наталья", "Светлана"]
student_surname = ["Иванов", "Петров", "Васильев", "Морозов", "Тягунов", "Романов", "Корнев", "Кузнецов", "Михайлов",
                   "Смирнов", "Попов", "Карпов", "Гуляев", "Маслов"]
student_father_name = ["Иванович", "Олегович", "Васильевич", "Евгеньевич", "Константинович", "Викторович",
                       "Александрович", "Антонович", "Игоревич", "Дмитриевич", "Владиславович", "Даниилович",
                       "Михайлович", "Арсеньевич"]

def generate(course, group_name, group_number):
    inc = (group_number * course) - 1
    if group_number == 1 and course == 2: inc = 2  # чтобы не усложнять формулу ниже
    cipher_counter = 1000 + (100 * inc)  # шифр студента, с запасом чтобы добавлять новых
    for i in range(20):  # в группе 20 студентов

        #########################################   ФОРМИРОВАНИЕ СПИСКА ГРУППЫ   #######################################

        gender = random.randint(0, 1)  # выбор пола студента, 0 - мужской, 1 - женский
        if gender == 0:
            card = {'student cipher': cipher_counter,  # карточка с данными о студенте, экзамене и результатах экзамена
                    'student name': random.choice(student_male_name),
                    'surname': random.choice(student_surname),
                    'father name': random.choice(student_father_name),
                    'course': course,
                    'group': group_name
                    }
        else:
            card = {'student cipher': cipher_counter,
                    'student name': random.choice(student_female_name),
                    'surname': random.choice(student_surname) + 'а',
                    'father name': random.choice(student_father_name)[:-2] + 'на',
                    'course': course,
                    'group': group_name
                    }

        ############################################   ОЦЕНКИ ЗА ЭКЗАМЕН   #############################################
        # для 1 курса шифр начинается с 2000, для 2 курса с 2100
        if course == 1:
            exam_info = {'date': '10.01.23',
                         'hours': 200,
                         'subject cipher': 2000,
                         'subject name': 'Информационные системы в мехатронике и робототехнике',
                         'mark': random.randint(2, 5)
                         }
            card.update(exam_info)  # update лучше вообще не делать
            es.index(index="database", body=card)  # для каждого нового экзамена/зачёта данные перезпаисываются,
            # а данные студента остаются

            exam_info = {'date': '12.01.23',
                         'hours': 200,
                         'subject cipher': 2001,
                         'subject name': 'Агентно-ориентированные системы управления',
                         'mark': random.randint(2, 5)
                         }
            card.update(exam_info)
            es.index(index="database", body=card)

            exam_info = {'date': '14.01.23',
                         'hours': 200,
                         'subject cipher': 2002,
                         'subject name': 'Методы и теория оптимизации',
                         'mark': random.randint(2, 5)
                         }
            card.update(exam_info)
            es.index(index="database", body=card)

        elif course == 2:
            exam_info = {'date': '10.01.23',
                         'hours': 200,
                         'subject cipher': 2100,
                         'subject name': 'Автоматизация настройки систем управления интеллектуальных мобильных роботов',
                         'mark': random.randint(2, 5)
                         }
            card.update(exam_info)
            es.index(index="database", body=card)

            exam_info = {'date': '12.01.23',
                         'hours': 200,
                         'subject cipher': 2101,
                         'subject name': 'Системы автоматизированного проектирования и производства',
                         'mark': random.randint(2, 5)
                         }
            card.update(exam_info)
            es.index(index="database", body=card)

            exam_info = {'date': '14.01.23',
                         'hours': 200,
                         'subject cipher': 2102,
                         'subject name': 'Интеллектуальные технологии локальной навигации',
                         'mark': random.randint(2, 5)
                         }
            card.update(exam_info)
            es.index(index="database", body=card)

        #############################################   ОЦЕНКИ ЗА ЗАЧЁТ   ##############################################
        # для 1 курса шифр начинается с 3000, для 2 курса с 3100
        if course == 1:  # 0 - зачет не сдан, 1 - сдан
            zachet_info = {'date': '20.12.22',
                           'hours': 150,
                           'subject cipher': 3000,
                           'subject name': 'Теория игр в управлении роботами',
                           'mark': random.choice([0, 1, 1, 1, 1])
                           }
            card.update(zachet_info)
            es.index(index="database", body=card)

            zachet_info = {'date': '22.12.22',
                           'hours': 150,
                           'subject cipher': 3001,
                           'subject name': 'Статистическая динамика автоматических систем',
                           'mark': random.choice([0, 1, 1, 1, 1])
                           }
            card.update(zachet_info)
            es.index(index="database", body=card)

            zachet_info = {'date': '24.12.22',
                           'hours': 150,
                           'subject cipher': 3002,
                           'subject name': 'Коммуникативные технологии в профессиональной сфере на иностранном языке',
                           'mark': random.choice([0, 1, 1, 1, 1])
                           }
            card.update(zachet_info)
            es.index(index="database", body=card)

            zachet_info = {'date': '26.12.22',
                           'hours': 150,
                           'subject cipher': 3003,
                           'subject name': 'Системный подход в научно-проектной деятельности',
                           'mark': random.choice([0, 1, 1, 1, 1])
                           }
            card.update(zachet_info)
            es.index(index="database", body=card)

        elif course == 2:
            zachet_info = {'date': '20.12.22',
                           'hours': 150,
                           'subject cipher': 3100,
                           'subject name': 'Технологии обработки информации в интеллектуальных мобильных роботах',
                           'mark': random.choice([0, 1, 1, 1, 1])
                           }
            card.update(zachet_info)
            es.index(index="database", body=card)

            zachet_info = {'date': '22.12.22',
                           'hours': 150,
                           'subject cipher': 3101,
                           'subject name': 'Теория эксперимента в исследованиях систем',
                           'mark': random.choice([0, 1, 1, 1, 1])
                           }
            card.update(zachet_info)
            es.index(index="database", body=card)

            zachet_info = {'date': '24.12.22',
                           'hours': 150,
                           'subject cipher': 3102,
                           'subject name': 'Бизнес технологии цифрового производства',
                           'mark': random.choice([0, 1, 1, 1, 1])
                           }
            card.update(zachet_info)
            es.index(index="database", body=card)

            zachet_info = {'date': '26.12.22',
                           'hours': 150,
                           'subject cipher': 3103,
                           'subject name': 'Управление проектами по созданию сложных технических систем',
                           'mark': random.choice([0, 1, 1, 1, 1])
                           }
            card.update(zachet_info)
            es.index(index="database", body=card)

        cipher_counter += 1

es.indices.create(index="database")  # создание индекса

generate(1, 'КРМО-01-22', 1)  # генерирует список групп, оценки за экзамен, зачёты
generate(1, 'КРМО-02-22', 2)
generate(2, 'КРМО-01-21', 1)
generate(2, 'КРМО-02-21', 2)
