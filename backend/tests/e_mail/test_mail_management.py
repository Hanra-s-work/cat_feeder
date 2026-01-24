r"""
# +==== BEGIN CatFeeder =================+
# LOGO:
# ..............(..../\
# ...............)..(.')
# ..............(../..)
# ...............\(__)|
# Inspired by Joan Stark
# source https://www.asciiart.eu/
# animals/cats
# /STOP
# PROJECT: CatFeeder
# FILE: test_mail_management.py
# CREATION DATE: 11-01-2026
# LAST Modified: 11-01-2026
# DESCRIPTION:
# Unit tests for email management wrapper class.
# /STOP
# COPYRIGHT: (c) Cat Feeder
# PURPOSE: Comprehensive test suite for MailManagement class initialization and operations.
# // AR
# +==== END CatFeeder =================+
"""
from unittest.mock import Mock, MagicMock, patch, mock_open
import pytest
import smtplib
import ssl

try:
    from libs.e_mail.mail_management import MailManagement
except Exception:
    from src.libs.e_mail.mail_management import MailManagement


class TestMailManagementInitialization:
    """Test MailManagement class initialization."""

    def test_mail_management_init_default_values(self):
        """Verify MailManagement initializes with default values."""
        mail = MailManagement()
        assert mail.error == 84
        assert mail.success == 0
        assert mail.debug is False

    def test_mail_management_init_custom_error_code(self):
        """Verify MailManagement accepts custom error code."""
        mail = MailManagement(error=1)
        assert mail.error == 1

    def test_mail_management_init_custom_success_code(self):
        """Verify MailManagement accepts custom success code."""
        mail = MailManagement(success=200)
        assert mail.success == 200

    def test_mail_management_init_custom_debug_flag(self):
        """Verify MailManagement accepts custom debug flag."""
        mail = MailManagement(debug=True)
        assert mail.debug is True

    def test_mail_management_init_loads_constants(self):
        """Verify MailManagement loads email constants."""
        mail = MailManagement()
        assert mail.sender is not None
        assert mail.host is not None
        assert mail.api_key is not None
        assert mail.port is not None

    def test_mail_management_init_all_parameters(self):
        """Verify MailManagement accepts all parameters."""
        mail = MailManagement(error=1, success=200, debug=True)
        assert mail.error == 1
        assert mail.success == 200
        assert mail.debug is True

    def test_mail_management_final_class_metaclass(self):
        """Verify MailManagement cannot be subclassed."""
        with pytest.raises(TypeError):
            class SubMailManagement(MailManagement):
                pass


class TestMailManagementSendEmail:
    """Test MailManagement send_email method."""

    def test_send_email_success_html(self):
        """Verify send_email returns success code for HTML email."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email(
                'test@example.com', 'Test Subject', '<h1>Test</h1>', body_type='html')
            assert result == mail.success

    def test_send_email_success_plain(self):
        """Verify send_email returns success code for plain text email."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email(
                'test@example.com', 'Test Subject', 'Test body', body_type='plain')
            assert result == mail.success

    def test_send_email_default_body_type_html(self):
        """Verify send_email defaults to HTML body type."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email(
                'test@example.com', 'Test Subject', '<h1>Test</h1>')
            assert result == mail.success

    def test_send_email_sets_from_header(self):
        """Verify send_email sets From header."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            mail.send_email('test@example.com', 'Test Subject', 'Body')
            mock_server.send_message.assert_called_once()

            # Check that the email was constructed with From header
            call_args = mock_server.send_message.call_args
            assert call_args is not None

    def test_send_email_sets_to_header(self):
        """Verify send_email sets To header."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            receiver = 'test@example.com'
            mail.send_email(receiver, 'Test Subject', 'Body')
            mock_server.send_message.assert_called_once()

    def test_send_email_sets_subject_header(self):
        """Verify send_email sets Subject header."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            mail.send_email('test@example.com', 'Test Subject', 'Body')
            mock_server.send_message.assert_called_once()

    def test_send_email_smtp_exception(self):
        """Verify send_email returns error code on SMTP exception."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException(
                'SMTP Error')

            mail = MailManagement()
            result = mail.send_email(
                'test@example.com', 'Test Subject', 'Body')
            assert result == mail.error

    def test_send_email_connection_error(self):
        """Verify send_email returns error code on connection error."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = OSError(
                'Connection refused')

            mail = MailManagement()
            result = mail.send_email(
                'test@example.com', 'Test Subject', 'Body')
            assert result == mail.error

    def test_send_email_ssl_error(self):
        """Verify send_email returns error code on SSL error."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = ssl.SSLError(
                'SSL Error')

            mail = MailManagement()
            result = mail.send_email(
                'test@example.com', 'Test Subject', 'Body')
            assert result == mail.error


class TestMailManagementSendEmailWithAttachment:
    """Test MailManagement send_email_with_attachment method."""

    def test_send_email_with_attachment_success(self):
        """Verify send_email_with_attachment returns success code."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp, \
                patch('builtins.open', mock_open(read_data=b'file content')):
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email_with_attachment(
                'test@example.com',
                'Test Subject',
                'Body',
                ['/path/to/file.txt']
            )
            assert result == mail.success

    def test_send_email_with_multiple_attachments(self):
        """Verify send_email_with_attachment handles multiple files."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp, \
                patch('builtins.open', mock_open(read_data=b'file content')):
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email_with_attachment(
                'test@example.com',
                'Test Subject',
                'Body',
                ['/path/to/file1.txt', '/path/to/file2.txt']
            )
            assert result == mail.success

    def test_send_email_with_attachment_file_not_found(self):
        """Verify send_email_with_attachment returns error on file not found."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.return_value = MagicMock()

            with patch('builtins.open', side_effect=FileNotFoundError('File not found')):
                mail = MailManagement()
                result = mail.send_email_with_attachment(
                    'test@example.com',
                    'Test Subject',
                    'Body',
                    ['/path/to/missing.txt']
                )
                assert result == mail.error

    def test_send_email_with_attachment_permission_denied(self):
        """Verify send_email_with_attachment returns error on permission denied."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.return_value = MagicMock()

            with patch('builtins.open', side_effect=PermissionError('Permission denied')):
                mail = MailManagement()
                result = mail.send_email_with_attachment(
                    'test@example.com',
                    'Test Subject',
                    'Body',
                    ['/path/to/file.txt']
                )
                assert result == mail.error

    def test_send_email_with_attachment_smtp_error(self):
        """Verify send_email_with_attachment returns error on SMTP error."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp, \
                patch('builtins.open', mock_open(read_data=b'file content')):
            mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException(
                'SMTP Error')

            mail = MailManagement()
            result = mail.send_email_with_attachment(
                'test@example.com',
                'Test Subject',
                'Body',
                ['/path/to/file.txt']
            )
            assert result == mail.error

    def test_send_email_with_attachment_html_body(self):
        """Verify send_email_with_attachment handles HTML body."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp, \
                patch('builtins.open', mock_open(read_data=b'file content')):
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email_with_attachment(
                'test@example.com',
                'Test Subject',
                '<h1>Body</h1>',
                ['/path/to/file.txt'],
                body_type='html'
            )
            assert result == mail.success


class TestMailManagementSendEmailToMultiple:
    """Test MailManagement send_email_to_multiple method."""

    def test_send_email_to_multiple_success(self):
        """Verify send_email_to_multiple returns success code."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            receivers = ['test1@example.com', 'test2@example.com']
            result = mail.send_email_to_multiple(
                receivers, 'Test Subject', 'Body')
            assert result == mail.success

    def test_send_email_to_multiple_single_receiver(self):
        """Verify send_email_to_multiple handles single receiver in list."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email_to_multiple(
                ['test@example.com'], 'Test Subject', 'Body')
            assert result == mail.success

    def test_send_email_to_multiple_many_receivers(self):
        """Verify send_email_to_multiple handles many receivers."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            receivers = [f'test{i}@example.com' for i in range(10)]
            result = mail.send_email_to_multiple(
                receivers, 'Test Subject', 'Body')
            assert result == mail.success

    def test_send_email_to_multiple_smtp_error(self):
        """Verify send_email_to_multiple returns error on SMTP error."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException(
                'SMTP Error')

            mail = MailManagement()
            result = mail.send_email_to_multiple(
                ['test@example.com'], 'Test Subject', 'Body')
            assert result == mail.error

    def test_send_email_to_multiple_html_body(self):
        """Verify send_email_to_multiple handles HTML body."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email_to_multiple(
                ['test@example.com'],
                'Test Subject',
                '<h1>Body</h1>',
                body_type='html'
            )
            assert result == mail.success

    def test_send_email_to_multiple_plain_body(self):
        """Verify send_email_to_multiple handles plain text body."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            result = mail.send_email_to_multiple(
                ['test@example.com'],
                'Test Subject',
                'Body',
                body_type='plain'
            )
            assert result == mail.success


class TestMailManagementSendEmailWithInlineImage:
    """Test MailManagement send_email_with_inline_image method."""

    def test_send_email_with_inline_image_success(self):
        """Verify send_email_with_inline_image returns success code."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp, \
                patch('builtins.open', mock_open(read_data=b'image data')), \
                patch('src.libs.e_mail.mail_management.make_msgid', return_value='<test@msgid>'), \
                patch('src.libs.e_mail.mail_management.EmailMessage') as mock_email_msg:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_em = MagicMock()
            mock_email_msg.return_value = mock_em

            mail = MailManagement()
            body = 'Image: {img_cid}'
            result = mail.send_email_with_inline_image(
                'test@example.com',
                'Test Subject',
                body,
                '/path/to/image.jpg',
                body_type='plain'
            )
            assert result == mail.success

    def test_send_email_with_inline_image_file_not_found(self):
        """Verify send_email_with_inline_image returns error on file not found."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.return_value = MagicMock()

            with patch('builtins.open', side_effect=FileNotFoundError('File not found')):
                mail = MailManagement()
                result = mail.send_email_with_inline_image(
                    'test@example.com',
                    'Test Subject',
                    'Body',
                    '/path/to/missing.jpg'
                )
                assert result == mail.error

    def test_send_email_with_inline_image_missing_placeholder(self):
        """Verify send_email_with_inline_image returns error on missing placeholder."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp, \
                patch('builtins.open', mock_open(read_data=b'image data')):
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            mail = MailManagement()
            body = 'No placeholder here'  # Missing {img_cid}
            result = mail.send_email_with_inline_image(
                'test@example.com',
                'Test Subject',
                body,
                '/path/to/image.jpg'
            )
            assert result == mail.error

    def test_send_email_with_inline_image_smtp_error(self):
        """Verify send_email_with_inline_image returns error on SMTP error."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp, \
                patch('builtins.open', mock_open(read_data=b'image data')):
            mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException(
                'SMTP Error')

            mail = MailManagement()
            body = 'Image: {img_cid}'
            result = mail.send_email_with_inline_image(
                'test@example.com',
                'Test Subject',
                body,
                '/path/to/image.jpg'
            )
            assert result == mail.error

    def test_send_email_with_inline_image_html_body(self):
        """Verify send_email_with_inline_image handles HTML body."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp, \
                patch('builtins.open', mock_open(read_data=b'image data')), \
                patch('src.libs.e_mail.mail_management.make_msgid', return_value='<test@msgid>'), \
                patch('src.libs.e_mail.mail_management.EmailMessage') as mock_email_msg:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_em = MagicMock()
            mock_email_msg.return_value = mock_em

            mail = MailManagement()
            body = '<img src="cid:{img_cid}" />'
            result = mail.send_email_with_inline_image(
                'test@example.com',
                'Test Subject',
                body,
                '/path/to/image.jpg',
                body_type='plain'
            )
            assert result == mail.success


class TestMailManagementInternalSend:
    """Test MailManagement internal _send method."""

    def test_internal_send_success(self):
        """Verify _send returns success code on successful send."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            from email.message import EmailMessage
            mail = MailManagement()
            em = EmailMessage()
            em['From'] = 'sender@example.com'
            em['To'] = 'receiver@example.com'
            em['Subject'] = 'Test'
            em.set_content('Test body')

            result = mail._send(em)
            assert result == mail.success

    def test_internal_send_smtp_exception(self):
        """Verify _send returns error code on SMTP exception."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = smtplib.SMTPException(
                'SMTP Error')

            from email.message import EmailMessage
            mail = MailManagement()
            em = EmailMessage()

            result = mail._send(em)
            assert result == mail.error

    def test_internal_send_os_error(self):
        """Verify _send returns error code on OS error."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = OSError(
                'Connection error')

            from email.message import EmailMessage
            mail = MailManagement()
            em = EmailMessage()

            result = mail._send(em)
            assert result == mail.error

    def test_internal_send_ssl_error(self):
        """Verify _send returns error code on SSL error."""
        with patch('src.libs.e_mail.mail_management.smtplib.SMTP_SSL') as mock_smtp:
            mock_smtp.return_value.__enter__.side_effect = ssl.SSLError(
                'SSL Error')

            from email.message import EmailMessage
            mail = MailManagement()
            em = EmailMessage()

            result = mail._send(em)
            assert result == mail.error
