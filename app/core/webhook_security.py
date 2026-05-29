import hashlib
from typing import Dict, Any
from app.core.config import settings


def generate_signature(data: Dict[str, Any]) -> str:
    """
    Генерация подписи для вебхука
    """
    filtered_data = {k: v for k, v in data.items() if k != 'signature'}

    sorted_keys = sorted(filtered_data.keys())

    hash_string = ''.join(str(filtered_data[key]) for key in sorted_keys)
    hash_string += settings.WEBHOOK_SECRET_KEY

    signature = hashlib.sha256(hash_string.encode()).hexdigest()

    return signature


def verify_signature(data: Dict[str, Any]) -> bool:
    """
    Проверка подписи вебхука
    """
    provided_signature = data.get('signature')
    if not provided_signature:
        return False

    expected_signature = generate_signature(data)
    return provided_signature == expected_signature