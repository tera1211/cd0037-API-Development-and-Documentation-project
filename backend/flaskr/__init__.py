import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import db,setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
def paginate_questions(request,selection):
    page = request.args.get('page',1,type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions



#convert categories to dict
def get_categories_dict():
    data = Category.query.all()

    if len(data) == 0:
        abort(404)

    categories_dict = {str(category.id): category.type for category in data}

    return categories_dict

#return questions json
def questions_json(current_category,selection):
    current_questions= paginate_questions(request,selection)
    categories_dict=get_categories_dict()

    if len(current_questions) == 0:
        abort(404)
    
    return jsonify({
        "questions":current_questions,
        "total_questions":len(selection),
        "categories":categories_dict,
        "current_category":current_category
    })

#get all questions
def get_all_questions():
    selection = Question.query.all()
    current_category='All'
    return questions_json(current_category,selection)

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    #Set up CORS. Allow '*' for origins. 
    CORS(app,resources={r"/*": {"origins": "*"}})
    
    # Use the after_request decorator to set Access-Control-Allow    
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers","Content-Type,Authorization,True"
        )
        response.headers.add(
            "Access-Contol-Allow-Methods","GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    
    #endpoint to handle GET requests for all available categories.
    @app.route('/categories')
    def retrieve_categories():
        categories_dict = get_categories_dict()

        return jsonify({
            "categories": categories_dict
        })
    
    #endpoint to handle GET requests for all the questions
    @app.route('/questions')
    def retrieve_questions():
        return get_all_questions()

    #endpoint to handle DELETE requests for question
    @app.route('/questions/<int:question_id>',methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()
            if question is None:
                abort(404)
            
            question.delete()
            return get_all_questions()

        except:
            abort(422)

    #endpoint to POST a new question
    @app.route('/questions',methods=['POST'])
    def create_post():
        body = request.get_json()

        new_question=body.get('question')
        new_answer=body.get('answer')
        new_difficulty=body.get('difficulty')
        new_category=body.get('category')

        try:
            question=Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
            question.insert()
            question_id=question.id

            selection = Question.query.all()
            current_category='All'
            current_questions= paginate_questions(request,selection)
            categories_dict=get_categories_dict()

            if len(current_questions) == 0:
                abort(404)
            
            return jsonify({
                "questions":current_questions,
                "total_questions":len(selection),
                "categories":categories_dict,
                "current_category":current_category,
                "id":question_id
            })
        except ValueError as e:
            abort(422)


    #POST endpoint to get questions based on a search term
    @app.route('/questions/search',methods=['POST'])
    def search_question():
        body = request.get_json()
        search_term=body.get('searchTerm')

        try:
            selection=Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
            current_category="All"
            return questions_json(current_category,selection)
        except:
            abort(404)

    #GET endpoint to get questions based on category
    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_in_category(category_id):
        try:
            selection = Question.query.filter_by(category = category_id).all()
            current_category = Category.query.get(category_id).type
            return questions_json(current_category,selection)
        except:
            abort(404)

    #POST endpoint to get questions to play the quiz
    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():
        body=request.get_json()

        previous_questions=body.get('previous_question')
        quiz_category=body.get('quiz_category')

        try:
            if quiz_category==0:
                if previous_questions is None:
                    questions= Question.query.all()
                else:
                    questions= Question.query.filter(Question.id.notin_(previous_questions)).all()
            else:
                if previous_questions is None:
                    questions= Question.query.filter(Question.category==quiz_category).all()
                else:
                    questions= Question.query.filter(Question.category==quiz_category,Question.id.notin_(previous_questions)).all()

            if len(questions) > 0:
                next_question = random.choice(questions).format()
            else:
                next_question = None
                
            return jsonify({
                'question': next_question
            })
        
        except ValueError as e:
            abort(422)
            print(e)


    #error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success':False,
            'error':404,
            'message':'resource not found'
        }),404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success':False,
            'error':422,
            'message':'unprocessable'
        }),422

    return app

