import json

'''# example dictionary that contains data like you want to have in json
dic = {'age': 100, 'name': 'mkyong.com', 'messages': ['msg 1', 'msg 2', 'msg 3']}

# get json string from that dictionary

with open('resreve.json', 'r') as f:
    json_safe = json.loads(f.read())

json_safe["2"] = dic

with open('resreve.json', 'w') as f:

    f.write(json.dumps(json_safe))'''

a = {'a': 110}
b = {'b' : 120}
a.update(b)
print(a)