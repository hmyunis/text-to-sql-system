from django.test import TestCase
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from django.urls import reverse

class AmharicTranslationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('ask_question')  # Assuming the URL name is 'ask_question' - need to check urls.py

    @patch('api.views.Client')
    @patch('api.views.execute_query')
    def test_amharic_translation(self, mock_execute, mock_client):
        # Mock HF Client
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.predict.return_value = "SELECT * FROM output"
        
        # Mock DB Execution
        mock_execute.return_value = {"columns": ["id"], "data": [[1]]}

        # 1. Send Amharic Request
        amharic_question = "ደንበኞችን አሳይ" # Show customers
        response = self.client.post('/api/ask/', {"question": amharic_question}, format='json')

        # 2. Check that it succeeded
        self.assertEqual(response.status_code, 200)

        # 3. Verify that predict was called with English text
        # We can't know the EXACT translation, so we check if it's NOT the Amharic text
        # and ideally contains "customers" or "show" in English
        args, _ = mock_instance.predict.call_args
        predicted_text = args[0]
        
        print(f"Original: {amharic_question}")
        print(f"Translated sent to model: {predicted_text}")

        self.assertNotEqual(predicted_text, amharic_question)
        # Check for English words roughly
        self.assertTrue("customer" in predicted_text.lower() or "show" in predicted_text.lower())
