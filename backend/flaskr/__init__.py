import os
from flask import Flask, request, abort, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

# from .flaskr import "_init_"
from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={"/": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        if (len(categories_dict) == 0):
            abort(404)
        return jsonify({
            'success': True,
            'categories': categories_dict
        })

    @app.route('/questions/<int:page_num>')
    def get_questions(page_num):
        get_questions = Question.query.all()
        get_categories = Category.query.order_by('id').all()
        total_questions = len(get_questions)
        page = Question.query.paginate(
            per_page=10, page=page_num, error_out=True)
        categories = []
        for c in get_categories:
            categories.append({
                'id': c.id,
                'type': c.type
            })
        questions = []
        for q in page.items:
            questions.append({
                'id': q.id,
                'question': q.question,
                'category': q.category,
                'answer': q.answer,
                'difficulty': q.difficulty,
                'type': Category.query.filter_by(id=q.category).first().type
            })
        return jsonify({
            'success': True,
            'categories': categories,
            'questions': questions,
            'total_questions': total_questions
            # 'current_category':current_category
        })

    @app.route('/categories/<int:id>/questions')
    def getByCategory(id):
        current_category = Category.query.filter_by(id=id).first()
        get_questions = Question.query.filter_by(category=id).all()
        questions = []
        for q in get_questions:
            questions.append({
                'id': q.id,
                'question': q.question,
                'category': q.category,
                'answer': q.answer,
                'difficulty': q.difficulty,
                'type': Category.query.filter_by(id=q.category).first().type
            })
        total_questions = len(get_questions)
        return jsonify({
            'success': True,
            'current_category': current_category.type,
            'questions': list(questions),
            'total_questions': total_questions
        })

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def del_question(id):
        error = False
        try:
            question = Question.query.filter_by(id=id).delete()
            db.session.commit()
        except:
            db.session.rollback()
            abort(404)
        finally:
            db.session.close()
            return jsonify({
                'success': True
            })

    @app.route('/questions', methods=['POST'])
    def searchQuestion():
        search = request.get_json()["searchTerm"]
        if search:
            get_questions = Question.query.filter(
                Question.question.ilike(f'%{search}%')).all()
            questions = []
            for q in get_questions:
                questions.append({
                    'id': q.id,
                    'question': q.question,
                    'category': q.category,
                    'answer': q.answer,
                    'difficulty': q.difficulty,
                    'type': Category.query.filter_by(id=q.category)
                    .first().type
                })
            total_questions = len(get_questions)
            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': total_questions
            })
        abort(404)

    @app.route('/questions/add', methods=['POST'])
    def addQuestion():
        error = False
        try:
            question = request.get_json()["question"]
            answer = request.get_json()["answer"]
            difficulty = request.get_json()["difficulty"]
            category = request.get_json()["category"]
            add = Question(
                question = question,
                answer = answer,
                category = category,
                difficulty  =difficulty
                )
            print(question)
            add.insert()
        except:
            error = True
        finally:
            return jsonify({
                'success': True,
                'question': question,
                'answer': answer,
                'difficulty': difficulty,
                'category': category
            })
        # abort(422)

    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        error = False
        try:
            category = request.get_json()["quiz_category"]
            previousQuestions = request.get_json()["previous_questions"]
            get_questions = ''
            print(category['id'])
            if category['id'] == 0:
                get_questions = Question.query.all()
            else:
                get_questions = Question.query.filter_by(
                    category=category['id']).all()
                questions = []
            for n in get_questions:
                questions.append({
                    'id': n.id,
                    'question': n.question,
                    'answer': n.answer
                })
                total_questions = len(questions)
        except:
            abort(422)
        finally:
            db.session.close()
        return jsonify({
            'success': True,
            'question': random.choice(questions),
            'previousQuestions': previousQuestions
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
