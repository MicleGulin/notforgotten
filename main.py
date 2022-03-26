import os
import sys
from random import randint

import requests
from flask import Flask, render_template, redirect, make_response, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_restful import abort
from requests import get

from data import db_session, people_api
from data.add_people import AddPeopleForm
from data.login_form import LoginForm
from data.users import User
from data.people import People
from data.register import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api_key = "40d1649f-0493-4b70-98ba-98533de7710b"
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/database.db")


@app.route('/human_show/<int:human_id>')
def human_show(human_id):
    human = get(f'http://localhost:5000/api/human/{human_id}').json()
    response = requests.get(
        f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}&geocode={human['human']['address']}&format=json")

    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = ','.join(toponym["Point"]["pos"].split())
        map = 'https://yandex.ru/maps/?ll=' + toponym_coodrinates + '&z=16'
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={toponym_coodrinates}&spn=0.03,0.03&l=map&pt=" \
                      f"{toponym_coodrinates},pm2gnm"
        city_map = requests.get(map_request)
        map_file = "static/img/map" + str(randint(1, 1000)) + ".png"
        # Возникли проблемы, связанные с кэшированием картинок в браузере клиента
        # Временное решение - создание случайных имен файлов и удаление уже созданных (чтобы не забивалась папка)
        for f in os.listdir("static/img"):
            os.remove("static/img/" + f)
        with open(map_file, "wb") as file:
            file.write(city_map.content)
            human['human']['place'] = "../" + map_file
    else:
        print("Ошибка выполнения запроса:")
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    return render_template('show_place.html', human=human, map=map)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        # if user and user.check_password(form.password.data):
        if user:
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    people = db_sess.query(People).all()
    names = {name.id: (name.surname, name.name) for name in users}
    return render_template("index.html", people=people, names=names, title='Карта')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="This user already exists")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            speciality=form.speciality.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addpeople', methods=['GET', 'POST'])
def addpeople():
    add_form = AddPeopleForm()
    if add_form.validate_on_submit():
        db_sess = db_session.create_session()
        human = People(
            surname=add_form.surname.data,
            name=add_form.name.data,
            patronymic=add_form.patronymic.data,
            address=add_form.address.data,
            info=add_form.info.data
        )
        db_sess.add(human)
        db_sess.commit()
        return redirect('/')
    return render_template('addpeople.html', title='Adding a people', form=add_form)


@app.route('/human/<int:id>', methods=['GET', 'POST'])
@login_required
def human_edit(id):
    form = AddPeopleForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        human = db_sess.query(People).filter(People.id == id).first()
        if human:
            form.surname.data = human.surname
            form.name.data = human.name
            form.patronymic.data = human.patronymic
            form.address.data = human.address
            form.info.data = human.info
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        human = db_sess.query(People).filter(People.id == id).first()
        if human:
            human.surname = form.surname.data
            human.name = form.name.data
            human.patronymic = form.patronymic.data
            human.address = form.address.data
            human.info = form.info.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('addpeople.html', title='Adding a people', form=form)


@app.route('/human_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def people_delete(id):
    db_sess = db_session.create_session()
    db_sess.query(People).filter(People.id == id).delete()
    db_sess.commit()

    return redirect('/')


def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(people_api.blueprint)

    app.run()


if __name__ == '__main__':
    main()
