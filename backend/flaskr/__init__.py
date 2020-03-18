import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  setup_db(app)
  
  # CORS - cross origin resource sharing
  cors = CORS(app, resources={r"/*": {"origins": "*"}})


  @app.after_request
  def after_request(response):
    response.headers.add('Acces-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Acess-Control-Allow-Methods', 'GET, POST, DELETE')
    return response

  @app.route('/categories', methods=['GET'])
  def categories():
    # all categories
    categories = Category.query.all()
    #json_categories = [category.format() for category in categories]
    #knowledge question id 76195
    json_categories = {category.id:category.type for category in categories}

    return jsonify({
      'success': True,
      'categories': json_categories,
      'total_categories': len(categories)
    }), 200
  
  @app.route('/questions', methods=['GET', 'POST'])
  def questions():
    if request.method == 'GET':
      page = request.args.get('page', 1, type=int)
      id_start = (page-1) * QUESTIONS_PER_PAGE
      id_end = id_start + QUESTIONS_PER_PAGE

      questions = Question.query.all()
      json_questions = [question.format() for question in questions]

      # why are categories submitted in questions request?
      categories = Category.query.all()
      json_categories = {category.id:category.type for category in categories}

      return jsonify({
        'success': True,
        'questions': json_questions[id_start:id_end],
        'total_questions': len(questions),
        'current_category': None, # knowledge question id 82424
        'categories': json_categories
      }), 200
    
    elif request.method == 'POST':
      parsed = request.get_json()
      if parsed:
        question = parsed.get('question')
        answer = parsed.get('answer')
        difficulty = parsed.get('difficulty')
        category = parsed.get('category')
      else:
        abort(417)

      if not question or not answer:
        abort(422)
      
      try:
        Question(question, answer, difficulty, category).insert()

        return jsonify({
          'success': True,
          'message': 'Question was created'
        }), 200
      except:
        abort(500)



    else:
      abort(405)

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).first()

    # out of index error if empty query
    if not question:
      abort(416)

    question.delete()

    return jsonify({
      'success': True,
      'message': 'Question was deleted'
    }), 200


  @app.route('/questions/stringsearch', methods=['POST'])
  def search_questions():
    page = request.args.get('page', 1, type=int)
    id_start = (page-1) * QUESTIONS_PER_PAGE
    id_end = id_start + QUESTIONS_PER_PAGE


    parsed = request.get_json()
    if parsed:
      search_term = parsed.get('searchTerm')
    else:
      abort(417)
    
    questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

    json_questions = [question.format() for question in questions]

    return jsonify({
      'success': True,
      'questions': json_questions[id_start:id_end],
      'total_questions': len(questions)
    }), 200

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def search_questions_by_cat(category_id):
    page = request.args.get('page', 1, type=int)
    id_start = (page-1) * QUESTIONS_PER_PAGE
    id_end = id_start + QUESTIONS_PER_PAGE

    #category_id why as string?
    questions = Question.query.filter_by(category=str(category_id)).all()
    json_questions = [question.format() for question in questions]

    return jsonify({
      'success': True,
      'questions': json_questions[id_start:id_end],
      'total_questions': len(questions)
    })

  @app.route('/quizzes', methods=['POST'])
  def start_quiz():
    previous_questions = request.json.get('previous_questions')
    current_category = request.json.get('quiz_category')['id']

    if current_category:
      questions = Question.query.filter_by(category=str(current_category)).filter(Question.id.notin_(previous_questions)).all()
    else:
      questions = Question.query.filter(Question.id.notin_(previous_questions)).all()

    if questions:
      remaining = len(questions)-1
      rnd = random.randint(0, remaining)
      print(rnd, remaining)
      json_question = questions[rnd].format()


      return jsonify({
      'success': True,
      'question': json_question,
      })
    else:
      return jsonify({
        'success': True,
      })


  @app.errorhandler(404)
  def not_found_error(error):
    
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Not found',
    }), 404
  
  @app.errorhandler(405)
  def method_error(error):
    
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method not allowed',
    }), 405


  @app.errorhandler(416)
  def out_of_range_error(error):

    return jsonify({
      'success': False,
      'error': 416,
      'message': 'Requested range not satisfiable',
    }), 416

  @app.errorhandler(417)
  def expect_error(error):

    return jsonify({
      'success': False,
      'error': 417,
      'message': 'Expecting application/json'
    }), 417

  @app.errorhandler(422)
  def unprocessable_error(error):

    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable Entity',
    }), 422

  @app.errorhandler(500)
  def internal_server_error(error):

    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server Error',
    }), 500

  
  return app

    