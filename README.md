# Email Validation API

This is a simple Flask API for validating email addresses. It provides a single endpoint to validate one or more emails.

## Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

1. Clone the repository and navigate to the project directory.

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

### Running the App

Start the development server:

```bash
flask run
```

The API will be available at `http://127.0.0.1:5000`.

---

## API Endpoint

### `POST /validate`

This endpoint validates a list of email addresses.

**Request Body:**

A JSON object containing a list of emails to validate.

```json
{
  "emails": ["email1@example.com", "email2@example.com"]
}
```

**Responses:**

- `200 OK`: Returns a list of validation results for each email.
- `400 Bad Request`: If the `emails` field is missing or not a list.

---

## Examples

### Example 1: Single Valid Email

**Request:**

```json
{
  "emails": ["test@example.com"]
}
```

**Response:**

```json
[
    {
        "MailboxValidation": {
            "Address": "test@example.com",
            "Evaluations": {
                "HasValidDnsRecords": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": true
                },
                "HasValidSyntax": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": true
                },
                "IsDisposableAddress": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": false
                },
                "IsRandomInput": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": false
                },
                "IsRoleAddress": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": false
                }
            },
            "IsValid": {
                "ConfidenceVerdict": "HIGH",
                "Value": true
            }
        }
    }
]
```

### Example 2: Bulk Validation with Mixed Results

**Request:**

```json
{
  "emails": ["test@example.com", "invalid-email"]
}
```

**Response:**

```json
[
    {
        "MailboxValidation": {
            "Address": "test@example.com",
            "Evaluations": {
                "HasValidDnsRecords": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": true
                },
                "HasValidSyntax": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": true
                },
                "IsDisposableAddress": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": false
                },
                "IsRandomInput": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": false
                },
                "IsRoleAddress": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": false
                }
            },
            "IsValid": {
                "ConfidenceVerdict": "HIGH",
                "Value": true
            }
        }
    },
    {
        "MailboxValidation": {
            "Address": "invalid-email",
            "Evaluations": {
                "HasValidDnsRecords": {
                    "ConfidenceVerdict": "NONE",
                    "Value": false
                },
                "HasValidSyntax": {
                    "ConfidenceVerdict": "HIGH",
                    "Value": false
                },
                "IsDisposableAddress": {
                    "ConfidenceVerdict": "NONE",
                    "Value": false
                },
                "IsRandomInput": {
                    "ConfidenceVerdict": "NONE",
                    "Value": false
                },
                "IsRoleAddress": {
                    "ConfidenceVerdict": "NONE",
                    "Value": false
                }
            },
            "IsValid": {
                "ConfidenceVerdict": "HIGH",
                "Value": false
            }
        }
    }
]
```

### Example 3: Error - Missing `emails` field

**Request:**

```json
{}
```

**Response:**

```json
{
  "error": "`emails` not provided"
}
```
