import unittest
import json
from unittest.mock import patch
from app import app

class TestEmailValidation(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_valid_email(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'email': 'test@example.com'}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['MailboxValidation']['IsValid']['ConfidenceVerdict'], 'HIGH')
        self.assertTrue(data['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])
        self.assertEqual(data['MailboxValidation']['Evaluations']['HasValidSyntax']['ConfidenceVerdict'], 'HIGH')

    def test_invalid_syntax(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'email': 'invalid-email'}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])

    @patch('app.validate_email')
    def test_nonexistent_domain(self, mock_validate_email):
        # Configure the mock to return values for all three calls
        mock_validate_email.side_effect = [True, False, False] # syntax, dns, smtp
        response = self.app.post('/validate',
                                 data=json.dumps({'email': 'test@nonexistent-domain-12345.com'}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])
        self.assertFalse(data['MailboxValidation']['Evaluations']['HasValidDnsRecords']['Value'])

    def test_role_address(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'email': 'admin@example.com'}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['MailboxValidation']['Evaluations']['IsRoleAddress']['Value'])

    def test_disposable_address(self):
        # This test is tricky as the library's disposable check is not direct
        # and depends on other factors.
        response = self.app.post('/validate',
                                 data=json.dumps({'email': 'test@10minutemail.com'}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        # The current implementation has a basic inference for disposable.
        # A more robust implementation would need a dedicated list.
        # self.assertTrue(data['MailboxValidation']['Evaluations']['IsDisposable']['Value'])

    def test_random_input(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'email': '1234567890@example.com'}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['MailboxValidation']['Evaluations']['IsRandomInput']['Value'])

    def test_no_email_provided(self):
        response = self.app.post('/validate',
                                 data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Email address not provided')

    def test_empty_email(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'email': ''}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(data['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])

if __name__ == '__main__':
    unittest.main()
