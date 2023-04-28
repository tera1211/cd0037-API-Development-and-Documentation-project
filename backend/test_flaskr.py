import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category,db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.app = create_app(self.database_path)
        self.client = self.app.test_client()
        self.new_question={
            'question':'What is the smallest unit of matter that retains the chemical properties of an element?',
            'answer':'Atom',
            'category':1,
            'difficulty':2
        }

        # binds the app to the current context
        with self.app.app_context():
        #     # create all tables
            db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            # db.drop_all()
            pass

    def test_get_categories(self):
        res = self.client.get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['categories']))

    def test_get_perginated_questions(self):
        res = self.client.get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'],'All')
    
    def test_404_beyond_valid_page(self):
        res = self.client.get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],'resource not found')
    
    def test_create_delete_question(self):
        with self.app.app_context():
            res = self.client.post('/questions',json=self.new_question)
            data=json.loads(res.data)
            question_id = data.get('id')
            self.assertEqual(res.status_code,200)
            # Confirm that the question was actually added to the database
            question = Question.query.filter(Question.id == question_id).one_or_none()
            self.assertIsNotNone(question)

            # Delete the question
            delete_res = self.client.delete(f'/questions/{question_id}')
            self.assertEqual(delete_res.status_code,200)

            # Confirm that the question was actually deleted from the database
            question = Question.query.filter(Question.id == question_id).one_or_none()
            self.assertIsNone(question)
    
    def test_422_delete_non_existing_question(self):
        with self.app.app_context():
            res = self.client.delete(f'/questions/1000000')
            data = json.loads(res.data)

            self.assertEqual(res.status_code,422)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'],'unprocessable')
    
    def test_search_question(self):
        data={
            'searchTerm': 'autobiography'
        }
        with self.app.app_context():
            res = self.client.post('/questions/search',json=data)
            data = json.loads(res.data)

            self.assertEqual(res.status_code,200)
            self.assertTrue(len(data['questions']))
    
    def test_404_non_existing_search(self):
        data={
            'searchTerm': 'this search term does not exist'
        }
        with self.app.app_context():
            res = self.client.post('/questions/search',json=data)
            data = json.loads(res.data)

            self.assertEqual(res.status_code,404)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'],'resource not found')
    
    def test_retrieve_questions_in_category(self):
        res = self.client.get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'],'Science')
    
    def test_404_retrieve_questions_in_category(self):
        res = self.client.get('/categories/10000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'],'resource not found')
    
    def test_play_quiz(self):
        data={
            'previous_question':[20],
            'quiz_category':1
        }
        with self.app.app_context():
            res = self.client.post('/quizzes',json=data)
            data = json.loads(res.data)
            self.assertEqual(res.status_code,200)
            self.assertTrue(len(data['question']))




    
    



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()