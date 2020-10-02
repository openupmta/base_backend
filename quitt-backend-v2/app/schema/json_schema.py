schema_user_create = {
    "type": "object",
    "properties": {
        "username": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "password": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "first_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "last_name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 50
        },
        "company": {
            "type": "string",
            "maxLength": 50
        },
        "address": {
            "type": "string",
            "maxLength": 50
        },
        "mobile": {
            "type": "string",
            "maxLength": 50
        }
    },
    "required": ["username", "password", "first_name", "last_name"]
}