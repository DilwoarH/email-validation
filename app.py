from flask import Flask, request, jsonify
from validate_email_address import validate_email
import re

app = Flask(__name__)

ROLE_ADDRESSES = [
    'admin', 'support', 'info', 'contact', 'sales', 'help', 'billing',
    'abuse', 'postmaster', 'webmaster', 'noreply', 'security'
]

def is_random_input(email):
    """
    A simple check for randomly generated email patterns.
    This is a basic implementation and can be expanded.
    """
    local_part = email.split('@')[0]

    if not local_part:
        return False

    # Check for long strings of numbers
    if re.search(r'\d{5,}', local_part):
        return True

    # Check for high ratio of non-alphanumeric characters (simple version)
    if len(local_part) > 0 and len(re.findall(r'[^a-zA-Z0-9]', local_part)) / len(local_part) > 0.5:
        return True

    # Check for lack of vowels (common in random strings)
    if not re.search(r'[aeiou]', local_part, re.IGNORECASE):
        return True

    return False

@app.route('/validate', methods=['POST'])
def validate_email_address():
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'error': 'Email address not provided'}), 400

    email = data['email']

    # 1. Syntax Validation
    has_valid_syntax = validate_email(email, check_smtp=False, check_dns=False)

    is_random = is_random_input(email)

    if not has_valid_syntax:
        return jsonify({
            "MailboxValidation": {
                "IsValid": {
                    "ConfidenceVerdict": "LOW"
                },
                "Evaluations": {
                    "HasValidSyntax": {
                        "Value": False,
                        "ConfidenceVerdict": "HIGH"
                    },
                    "HasValidDnsRecords": {
                        "Value": False,
                        "ConfidenceVerdict": "NONE"
                    },
                    "MailboxExists": {
                        "Value": False,
                        "ConfidenceVerdict": "NONE"
                    },
                    "IsRoleAddress": {
                        "Value": False,
                        "ConfidenceVerdict": "NONE"
                    },
                    "IsDisposable": {
                        "Value": False,
                        "ConfidenceVerdict": "NONE"
                    },
                    "IsRandomInput": {
                        "Value": is_random,
                        "ConfidenceVerdict": "LOW"
                    }
                }
            }
        })

    # 2. DNS Records
    has_valid_dns = validate_email(email, check_smtp=False, check_dns=True)

    # 3. Mailbox Existence (SMTP check)
    mailbox_exists = validate_email(email, check_smtp=True)

    # 4. Role Address
    local_part = email.split('@')[0]
    is_role_address = local_part.lower() in ROLE_ADDRESSES

    # 5. Disposable Domain
    is_disposable = not mailbox_exists and has_valid_dns and not has_valid_syntax

    # 6. Random String Patterns
    is_random = is_random_input(email)

    # Determine overall validity
    is_valid_confidence = "HIGH" if has_valid_syntax and has_valid_dns else "LOW"

    return jsonify({
        "MailboxValidation": {
            "IsValid": {
                "ConfidenceVerdict": is_valid_confidence
            },
            "Evaluations": {
                "HasValidSyntax": {
                    "Value": bool(has_valid_syntax),
                    "ConfidenceVerdict": "HIGH"
                },
                "HasValidDnsRecords": {
                    "Value": bool(has_valid_dns),
                    "ConfidenceVerdict": "MEDIUM"
                },
                "MailboxExists": {
                    "Value": bool(mailbox_exists),
                    "ConfidenceVerdict": "MEDIUM"
                },
                "IsRoleAddress": {
                    "Value": is_role_address,
                    "ConfidenceVerdict": "LOW"
                },
                "IsDisposable": {
                    "Value": is_disposable,
                    "ConfidenceVerdict": "LOW"
                },
                "IsRandomInput": {
                    "Value": is_random,
                    "ConfidenceVerdict": "LOW"
                }
            }
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
