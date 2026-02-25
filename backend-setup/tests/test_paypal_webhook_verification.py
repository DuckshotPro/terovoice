
import unittest
import json
import os
from unittest.mock import patch, MagicMock
from flask import Flask
from backend_setup.api.paypal_integration import paypal_bp

class TestPayPalWebhookVerification(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(paypal_bp)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('backend_setup.api.paypal_integration.get_paypal_access_token')
    @patch('backend_setup.api.paypal_integration.requests.post')
    @patch('backend_setup.api.paypal_integration.PAYPAL_WEBHOOK_ID', 'test_webhook_id')
    def test_verify_webhook_success(self, mock_post, mock_get_token):
        # Mock access token
        mock_get_token.return_value = 'mock_access_token'

        # Mock PayPal verification response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'verification_status': 'SUCCESS'}
        mock_post.return_value = mock_response

        # Webhook payload
        payload = {
            'id': 'WH-12345',
            'event_type': 'PAYMENT.CAPTURE.COMPLETED',
            'resource': {'id': 'I-12345'}
        }

        # Headers
        headers = {
            'PAYPAL-TRANSMISSION-ID': 'test_transmission_id',
            'PAYPAL-TRANSMISSION-TIME': '2023-10-27T10:00:00Z',
            'PAYPAL-CERT-URL': 'https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123',
            'PAYPAL-AUTH-ALGO': 'SHA256withRSA',
            'PAYPAL-TRANSMISSION-SIG': 'test_signature'
        }

        # Send request
        response = self.client.post(
            '/api/paypal/verify-webhook',
            json=payload,
            headers=headers
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['success'], True)

        # Verify mocked calls
        mock_get_token.assert_called_once()
        mock_post.assert_called_once()

        # Check if the verification request was constructed correctly
        call_args = mock_post.call_args
        self.assertIn('notifications/verify-webhook-signature', call_args[0][0])

        request_json = call_args[1]['json']
        self.assertEqual(request_json['transmission_id'], 'test_transmission_id')
        self.assertEqual(request_json['transmission_time'], '2023-10-27T10:00:00Z')
        self.assertEqual(request_json['cert_url'], 'https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123')
        self.assertEqual(request_json['auth_algo'], 'SHA256withRSA')
        self.assertEqual(request_json['transmission_sig'], 'test_signature')
        self.assertEqual(request_json['webhook_id'], 'test_webhook_id')
        self.assertEqual(request_json['webhook_event'], payload)

    @patch('backend_setup.api.paypal_integration.get_paypal_access_token')
    @patch('backend_setup.api.paypal_integration.requests.post')
    @patch('backend_setup.api.paypal_integration.PAYPAL_WEBHOOK_ID', 'test_webhook_id')
    def test_verify_webhook_failure(self, mock_post, mock_get_token):
        # Mock access token
        mock_get_token.return_value = 'mock_access_token'

        # Mock PayPal verification response - FAILURE
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'verification_status': 'FAILURE'}
        mock_post.return_value = mock_response

        # Webhook payload
        payload = {
            'id': 'WH-12345',
            'event_type': 'PAYMENT.CAPTURE.COMPLETED'
        }

        # Headers
        headers = {
            'PAYPAL-TRANSMISSION-ID': 'test_transmission_id',
            'PAYPAL-TRANSMISSION-TIME': '2023-10-27T10:00:00Z',
            'PAYPAL-CERT-URL': 'https://api.sandbox.paypal.com/v1/notifications/certs/CERT-123',
            'PAYPAL-AUTH-ALGO': 'SHA256withRSA',
            'PAYPAL-TRANSMISSION-SIG': 'test_signature'
        }

        # Send request
        response = self.client.post(
            '/api/paypal/verify-webhook',
            json=payload,
            headers=headers
        )

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    @patch('backend_setup.api.paypal_integration.get_paypal_access_token')
    def test_verify_webhook_missing_headers(self, mock_get_token):
        # Mock access token
        mock_get_token.return_value = 'mock_access_token'

        # Webhook payload
        payload = {
            'id': 'WH-12345',
            'event_type': 'PAYMENT.CAPTURE.COMPLETED'
        }

        # Missing headers
        headers = {}

        # Send request
        response = self.client.post(
            '/api/paypal/verify-webhook',
            json=payload,
            headers=headers
        )

        # Should fail due to missing headers or validation inside verify_webhook
        self.assertEqual(response.status_code, 400)
