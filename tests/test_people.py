from requests import get, post, delete

# Все люди
print(get('http://localhost:5000/api/people').json())

# Один не существующий человек
print(get('http://localhost:5000/api/human/120').json())

# Один существующий человек
print(get('http://localhost:5000/api/human/4').json())

# Добавить человека и проверить наличие
print(post('http://localhost:5000/api/human',
           json={'id': 12, 'surname': 'Сидоров', 'name': 'Константин', 'patronymic': 'Константинович',
                 'address': 'Москва Советская 50', 'info': 'Информации пока нет'}).json())
print(get('http://localhost:5000/api/human/12').json())

# Редактировать запись о человеке и проверить
print(post('http://localhost:5000/api/human/12',
           json={'id': 12, 'surname': 'Иванов', 'name': 'Константин', 'patronymic': 'Константинович',
                 'address': 'Москва, Советская, 50', 'info': 'Информация появилась'}).json())
print(get('http://localhost:5000/api/human/12').json())

# Удаление существующего человека и проверка
print(delete('http://localhost:5000/api/human/12').json())
print(get('http://localhost:5000/api/human/12').json())

# Удаление не существующего человека и проверка
print(delete('http://localhost:5000/api/human/12').json())
