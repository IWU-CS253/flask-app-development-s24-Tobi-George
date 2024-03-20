import os
import app as flaskr
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()
        with flaskr.app.app_context():
            flaskr.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(flaskr.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data

    def test_messages(self):
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here',
            category='A category'
        ), follow_redirects=True)
        assert b'No entries here so far' not in rv.data
        assert b'&lt;Hello&gt;' in rv.data
        assert b'<strong>HTML</strong> allowed here' in rv.data
        assert b'A category' in rv.data

    def test_delete_entry(self):
        rv_add = self.app.post('/add', data=dict(
            title='Test Entry',
            text='This is a test entry',
            category='Test Category'
        ), follow_redirects=True)

        with flaskr.app.app_context():
            db = flaskr.get_db()
            entry_id = db.execute('SELECT id FROM entries WHERE title = ?', ('Test Entry',)).fetchone()[0]

        rv_delete = self.app.post('/delete', data={'notes': entry_id}, follow_redirects=True)

        with flaskr.app.app_context():
            db = flaskr.get_db()
            deleted_entry = db.execute('SELECT * FROM entries WHERE id = ?', (entry_id,)).fetchone()
        self.assertIsNone(deleted_entry)


if __name__ == '__main__':
    unittest.main()
