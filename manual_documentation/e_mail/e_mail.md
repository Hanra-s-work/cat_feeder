<!-- 
-- +==== BEGIN CatFeeder =================+
-- LOGO: 
-- ..........####...####..........
-- ......###.....#.#########......
-- ....##........#.###########....
-- ...#..........#.############...
-- ...#..........#.#####.######...
-- ..#.....##....#.###..#...####..
-- .#.....#.##...#.##..##########.
-- #.....##########....##...######
-- #.....#...##..#.##..####.######
-- .#...##....##.#.##..###..#####.
-- ..#.##......#.#.####...######..
-- ..#...........#.#############..
-- ..#...........#.#############..
-- ...##.........#.############...
-- ......#.......#.#########......
-- .......#......#.########.......
-- .........#####...#####.........
-- /STOP
-- PROJECT: CatFeeder
-- FILE: e_mail.md
-- CREATION DATE: 02-12-2025
-- LAST Modified: 14:45:38 02-12-2025
-- DESCRIPTION: 
-- This is the project in charge of making the connected cat feeder project work.
-- /STOP
-- COPYRIGHT: (c) Cat Feeder
-- PURPOSE: An overview of the e-mail module for the server (smtp protocol).
-- // AR
-- +==== END CatFeeder =================+
-->
# Email Management Module

## Overview

The `e_mail` module provides a robust email management system for the CatFeeder application. The `MailManagement` class offers a simple yet powerful interface for sending emails with support for attachments, multiple recipients, HTML content, and inline images using SMTP over SSL.

## Architecture

![Email Management Architecture](e_mail_architecture.puml)

## Core Components

### MailManagement Class

The `MailManagement` class is the main component for email operations. It implements the `FinalClass` metaclass pattern to prevent inheritance and provides secure email sending capabilities.

**Key Features:**

- SMTP over SSL (port 465) for secure email transmission
- HTML and plain text email support
- File attachments with MIME encoding
- Multiple recipient support (To, Cc, Bcc)
- Inline image embedding
- Comprehensive error handling
- Debug logging integration

**Attributes:**

- `sender`: Email address of the sender (from environment)
- `host`: SMTP server hostname
- `api_key`: SMTP authentication password/API key
- `port`: SMTP port (default: 465 for SSL)
- `success`: Success return code (0)
- `error`: Error return code (84)
- `debug`: Debug mode flag

## Configuration

### Constants (mail_constants.py)

Email configuration is loaded from environment variables:

```python
# Environment Variables Required
SENDER_ADDRESS = os.getenv("EMAIL_SENDER_ADDRESS")
SENDER_HOST = os.getenv("EMAIL_SMTP_HOST")
SENDER_KEY = os.getenv("EMAIL_API_KEY")
SENDER_PORT = int(os.getenv("EMAIL_SMTP_PORT", "465"))
```

### Environment Setup

Create a `.env` file with the following variables:

```bash
EMAIL_SENDER_ADDRESS=noreply@Cat Feeder.com
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=465
EMAIL_API_KEY=your_smtp_password_or_api_key
```

## Usage Examples

### Basic Email Sending

```python
from backend.src.libs.e_mail import MailManagement

# Initialize the mail manager
mail_manager = MailManagement(debug=True)

# Send a simple HTML email
status = mail_manager.send_email(
    receiver="user@example.com",
    subject="Welcome to Cat Feeder",
    body="<h1>Hello!</h1><p>Welcome to our platform.</p>",
    body_type="html"
)

if status == 0:
    print("Email sent successfully")
else:
    print("Failed to send email")
```

### Plain Text Email

```python
# Send plain text email
status = mail_manager.send_email(
    receiver="user@example.com",
    subject="System Notification",
    body="This is a plain text notification message.",
    body_type="plain"
)
```

### Email with Attachments

```python
# Send email with multiple attachments
attachments = [
    "/path/to/report.pdf",
    "/path/to/invoice.xlsx",
    "/path/to/image.png"
]

status = mail_manager.send_email_with_attachment(
    receiver="client@example.com",
    subject="Monthly Report",
    body="<p>Please find attached your monthly report.</p>",
    attachments=attachments,
    body_type="html"
)
```

### Multiple Recipients

```python
# Send email to multiple recipients
recipients = [
    "user1@example.com",
    "user2@example.com",
    "admin@example.com"
]

status = mail_manager.send_email_to_multiple(
    receivers=recipients,
    subject="Team Announcement",
    body="<h2>Important Update</h2><p>Meeting at 3 PM today.</p>",
    body_type="html"
)
```

### Email with Inline Image

```python
# Send email with embedded image
html_body = """
<html>
<body>
    <h1>Check out our logo!</h1>
    <img src="cid:{img_cid}" alt="Company Logo">
    <p>Thank you for your business.</p>
</body>
</html>
"""

status = mail_manager.send_email_with_inline_image(
    receiver="customer@example.com",
    subject="Our New Logo",
    body=html_body,
    image_path="/path/to/logo.png",
    body_type="html"
)
```

### Error Handling Example

```python
# Comprehensive error handling
try:
    mail_manager = MailManagement(debug=True)
    
    status = mail_manager.send_email(
        receiver="test@example.com",
        subject="Test Email",
        body="Test message"
    )
    
    if status == mail_manager.error:
        print("Email sending failed - check logs for details")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Key Methods

### send_email(receiver, subject, body, body_type="html")

Sends a simple email to a single recipient.

**Parameters:**

- `receiver` (str): Recipient's email address
- `subject` (str): Email subject line
- `body` (str): Email content
- `body_type` (str): "html" or "plain" (default: "html")

**Returns:**

- `int`: Success (0) or error (84) code

**Example:**

```python
status = mail_manager.send_email(
    receiver="user@example.com",
    subject="Hello",
    body="<p>Hi there!</p>"
)
```

### send_email_with_attachment(receiver, subject, body, attachments, body_type="html")

Sends an email with one or more file attachments.

**Parameters:**

- `receiver` (str): Recipient's email address
- `subject` (str): Email subject line
- `body` (str): Email content
- `attachments` (List[str]): List of file paths to attach
- `body_type` (str): "html" or "plain" (default: "html")

**Returns:**

- `int`: Success (0) or error (84) code

**Features:**

- Automatically encodes files using Base64
- Handles multiple file types
- Preserves original filenames
- Validates file existence

### send_email_to_multiple(receivers, subject, body, body_type="html")

Sends an email to multiple recipients.

**Parameters:**

- `receivers` (List[str]): List of recipient email addresses
- `subject` (str): Email subject line
- `body` (str): Email content
- `body_type` (str): "html" or "plain" (default: "html")

**Returns:**

- `int`: Success (0) or error (84) code

### send_email_with_inline_image(receiver, subject, body, image_path, body_type="html")

Sends an email with an image embedded in the HTML body.

**Parameters:**

- `receiver` (str): Recipient's email address
- `subject` (str): Email subject line
- `body` (str): HTML body with `{img_cid}` placeholder
- `image_path` (str): Path to the image file
- `body_type` (str): "html" or "plain" (default: "html")

**Returns:**

- `int`: Success (0) or error (84) code

**Note:** The body must include `{img_cid}` placeholder for the image:

```html
<img src="cid:{img_cid}" alt="Image">
```

### _send(em)

Internal method that handles the actual SMTP connection and email transmission.

**Parameters:**

- `em` (EmailMessage): Prepared email message object

**Returns:**

- `int`: Success (0) or error (84) code

**Error Handling:**

- `smtplib.SMTPException`: SMTP protocol errors
- `OSError`: Network/file system errors
- `ssl.SSLError`: SSL/TLS connection errors

## Email Message Structure

The module uses Python's `email.message.EmailMessage` for email composition:

```python
em = EmailMessage()
em['From'] = sender
em['To'] = receiver
em['Subject'] = subject

# HTML content
em.add_alternative(html_body, subtype='html')

# Plain text content
em.set_content(plain_text_body)

# Attachments
em.add_attachment(file_data, maintype='application', 
                  subtype='octet-stream', filename='file.pdf')

# Inline images
em.add_related(img_data, maintype='image', 
               subtype='jpeg', cid=img_cid)
```

## Security Considerations

### SSL/TLS Encryption

The module uses `SMTP_SSL` for secure connections:

```python
context = ssl.create_default_context()
with smtplib.SMTP_SSL(self.host, self.port, context=context) as smtp:
    smtp.login(self.sender, self.api_key)
    smtp.send_message(em)
```

### Best Practices

1. **Store Credentials Securely**: Never hardcode email credentials
2. **Use Environment Variables**: Keep sensitive data in `.env` files
3. **Enable Debug Logging**: Use `debug=True` only in development
4. **Validate Inputs**: Always validate email addresses and file paths
5. **Handle Errors**: Check return codes and log failures
6. **Rate Limiting**: Implement rate limiting for bulk emails

## Error Handling

The module provides comprehensive error handling:

### Exception Types

- **SMTPException**: Authentication failures, protocol errors
- **OSError**: File not found, permission denied, network errors
- **SSLError**: SSL/TLS handshake failures
- **KeyError/ValueError**: Template formatting errors

### Error Logging

```python
# All errors are logged through the Disp logger
self.disp.log_critical(f"An error occurred sending email: {e}")
```

### Return Codes

- `0` (success): Email sent successfully
- `84` (error): Email sending failed (check logs)

## Integration Example

### FastAPI Endpoint

```python
from fastapi import FastAPI, HTTPException
from backend.src.libs.e_mail import MailManagement
from pydantic import BaseModel, EmailStr

app = FastAPI()
mail_manager = MailManagement(debug=False)

class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str

@app.post("/send-email")
async def send_email_endpoint(email: EmailRequest):
    status = mail_manager.send_email(
        receiver=email.to,
        subject=email.subject,
        body=email.body,
        body_type="html"
    )
    
    if status != 0:
        raise HTTPException(status_code=500, detail="Failed to send email")
    
    return {"message": "Email sent successfully"}
```

## Dependencies

- `smtplib`: SMTP protocol implementation
- `ssl`: SSL/TLS encryption
- `email`: Email message composition
- `display_tty`: Logging functionality
- Core modules (FinalClass)

## Testing

### Local Testing with Gmail

```python
# Configure for Gmail SMTP
EMAIL_SENDER_ADDRESS=your_email@gmail.com
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=465
EMAIL_API_KEY=your_app_specific_password
```

**Note:** Enable "App Passwords" in Gmail security settings for SMTP access.

## Troubleshooting

### Common Issues

1. **Authentication Failed**: Check API key and sender address
2. **Connection Timeout**: Verify SMTP host and port
3. **SSL Errors**: Ensure port 465 is used for SSL
4. **File Not Found**: Verify attachment paths exist
5. **HTML Not Rendering**: Check body_type is set to "html"

## See Also

- [Core Module Documentation](../core/core.md)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)
- [Email Package Documentation](https://docs.python.org/3/library/email.html)
