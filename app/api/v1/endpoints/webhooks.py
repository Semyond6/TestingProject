from fastapi import APIRouter, status
from app.api.deps import DBSession
from app.schemas.webhook import WebhookRequest, WebhookResponse
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/payment", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def payment_webhook(
        webhook_data: WebhookRequest,
        db: DBSession
):
    """
    Обработка вебхука от платежной системы

    - Проверяет подпись объекта
- Проверяет существование счета (создает если нет)
- Сохраняет транзакцию
- Начисляет сумму на счет
    """
    webhook_service = WebhookService(db)
    result = await webhook_service.process_webhook(webhook_data)
    return WebhookResponse(**result)