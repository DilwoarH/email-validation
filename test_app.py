import unittest
import json
from unittest.mock import patch
from app import app

class TestEmailValidation(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_single_valid_email(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': ['test@example.com']}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['MailboxValidation']['IsValid']['ConfidenceVerdict'], 'HIGH')
        self.assertTrue(data[0]['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])
        self.assertEqual(data[0]['MailboxValidation']['Evaluations']['HasValidSyntax']['ConfidenceVerdict'], 'HIGH')

    def test_single_invalid_syntax(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': ['invalid-email']}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertFalse(data[0]['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])

    @patch('app.validate_email')
    def test_nonexistent_domain(self, mock_validate_email):
        mock_validate_email.side_effect = [True, False, False]
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': ['test@nonexistent-domain-12345.com']}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertTrue(data[0]['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])
        self.assertFalse(data[0]['MailboxValidation']['Evaluations']['HasValidDnsRecords']['Value'])

    def test_role_address(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': ['admin@example.com']}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertTrue(data[0]['MailboxValidation']['Evaluations']['IsRoleAddress']['Value'])

    def test_disposable_address(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': ['test@10minutemail.com']}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_random_input(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': ['1234567890@example.com']}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertTrue(data[0]['MailboxValidation']['Evaluations']['IsRandomInput']['Value'])

    def test_no_emails_provided(self):
        response = self.app.post('/validate',
                                 data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], '`emails` not provided')

    def test_empty_emails_list(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': []}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], '`emails` should be a non-empty list')

    def test_bulk_email_validation(self):
        emails = ['test@example.com', 'invalid-email']
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': emails}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['MailboxValidation']['IsValid']['ConfidenceVerdict'], 'HIGH')
        self.assertFalse(data[1]['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])

    def test_empty_email_in_list(self):
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': ['']}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertFalse(data[0]['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])

    def test_bulk_email_validation_large(self):
        emails = [
            'test@example.com',
            'invalid-email',
            'another.valid@email.com',
            'and.another.one@domain.co.uk',
            '12345@numeric.com',
            'invalid-syntax@.com',
            'test@10minutemail.com',
            'admin@example.com',
            'test@nonexistent-domain-12345.com',
            'user+alias@gmail.com',
            'user@sub.domain.com',
            'user@.invalid.com',
            'user@domain-with-dash.com',
            'user@domain_with_underscore.com',
            'user@domain.c',
            'user@domain.company',
            'user@123.123.123.123',
            'user@[123.123.123.123]',
            'a@b.c',
            'very.long.local.part.that.is.perfectly.valid@example.com'
        ]
        response = self.app.post('/validate',
                                 data=json.dumps({'emails': emails}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 20)
        self.assertEqual(data[0]['MailboxValidation']['IsValid']['ConfidenceVerdict'], 'HIGH')
        self.assertFalse(data[1]['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])
        self.assertEqual(data[2]['MailboxValidation']['IsValid']['ConfidenceVerdict'], 'HIGH')
        self.assertFalse(data[5]['MailboxValidation']['Evaluations']['HasValidSyntax']['Value'])

if __name__ == '__main__':
    unittest.main()
