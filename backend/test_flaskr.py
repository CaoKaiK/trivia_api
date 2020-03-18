import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format('postgres','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass


    def test_get_categories(self):
        response = self.client().get('/categories')
        self.assertEqual(response.status_code, 200)
    
    def test_post_categories(self):    
        # fail post request
        response = self.client().post('/categories')
        self.assertEqual(response.status_code, 405)

    def test_get_questions(self):
        response = self.client().get('/questions')
        self.assertEqual(response.status_code, 200)

    def test_fail_post_questions(self):
        # fail post with missing json
        response = self.client().post('/questions')
        self.assertEqual(response.status_code, 417)
    
    def test_post_question(self):
        q = {
            'question': 'Question',
            'answer': 'Answer',
            'difficulty': '1',
            'category': '1'
        }

        response = self.client().post('/questions', json=q)
        self.assertEqual(response.status_code, 200)

    def test_fail_delete_question(self):
        response = self.client().delete('/questions/1000')
        self.assertEqual(response.status_code, 416)
    
    def test_delete_question(self):
        last_question = self.client().get('/questions').json['questions'][-1]['id']
        response = self.client().delete(f'/questions/{last_question}')
        self.assertEqual(response.status_code, 200)



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()