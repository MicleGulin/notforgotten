from flask import jsonify, Blueprint, request

from data import db_session
from data.people import People

blueprint = Blueprint('people_api', __name__, template_folder='templates')


# Информация о всех людях
@blueprint.route('/api/people')
def get_users():
    db_sess = db_session.create_session()
    people = db_sess.query(People).all()
    return jsonify({'People': [item.to_dict(
        only=('id', 'surname', 'name', 'patronymic', 'address', 'info')
    )
        for item in people]})


# Информация об одном человеке
@blueprint.route('/api/human/<int:human_id>', methods=['GET'])
def get_one_human(human_id):
    db_sess = db_session.create_session()
    human = db_sess.query(People).get(human_id)
    if not human:
        return jsonify({'error': 'Not found'})
    return jsonify({'human': human.to_dict(
        only=('id', 'surname', 'name', 'patronymic', 'address', 'info')
    )})


# Запись информации о новом человеке
@blueprint.route('/api/human', methods=['POST'])
def create_human():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['id', 'surname', 'name', 'patronymic', 'address', 'info']):
        return jsonify({'error': 'Bad request'})

    db_sess = db_session.create_session()
    human = People(
        id=request.json['id'],
        surname=request.json['surname'],
        name=request.json['name'],
        patronymic=request.json['patronymic'],
        address=request.json['address'],
        info=request.json['info']
    )

    if db_sess.query(People).filter(People.id == human.id).first():
        return jsonify({'error': 'Id already exists'})
    db_sess.add(human)
    db_sess.commit()
    return jsonify({'success': 'OK'})


# Редактирование информации о человеке
@blueprint.route('/api/human/<int:human_id>', methods=['POST'])
def edit_human(human_id):
    db_sess = db_session.create_session()
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['id', 'surname', 'name', 'patronymic', 'address', 'info']):
        return jsonify({'error': 'Bad request'})

    human = People(
        id=request.json['id'],
        surname=request.json['surname'],
        name=request.json['name'],
        patronymic=request.json['patronymic'],
        address=request.json['address'],
        info=request.json['info']
    )
    human_to_edit = db_sess.query(People).filter(People.id == human_id).first()
    if not human_to_edit:
        return jsonify({'error': 'Not found'})
    if human_to_edit:
        human_to_edit.id = human.id
        human_to_edit.surname = human.surname
        human_to_edit.name = human.name
        human_to_edit.patronymic = human.patronymic
        human_to_edit.address = human.address
        human_to_edit.info = human.info
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/human/<int:human_id>', methods=['DELETE'])
def delete_human(human_id):
    db_sess = db_session.create_session()
    human = db_sess.query(People).get(human_id)
    if not human:
        return jsonify({'error': 'Not found'})
    db_sess.delete(human)
    db_sess.commit()
    return jsonify({'success': 'OK'})
