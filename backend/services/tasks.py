import smtplib
from email.message import EmailMessage
from celery import shared_task
from backend.api.config import settings
from backend.finance.sync import sync_market_data
from starlette.templating import Jinja2Templates


@shared_task
def send_confirmation_email(to_email: str, token: str, username: str = "") -> None:
    confirmation_url = f"{settings.frontend_url}/confirm-email?token={token}"

    templates = Jinja2Templates(directory=settings.templates_dir)
    template = templates.get_template(name="verification_email.html")
    html_content = template.render(
        confirmation_url=confirmation_url,
        user=username,
    )

    message = EmailMessage()
    message.add_alternative(html_content, subtype="html")
    message["From"] = settings.email_settings.email_username
    message["To"] = to_email
    message["Subject"] = "Confirm your registration"

    with smtplib.SMTP_SSL(host=settings.email_settings.email_host, port=settings.email_settings.email_port) as smtp:
        smtp.login(
            user=settings.email_settings.email_username,
            password=settings.email_settings.email_password.get_secret_value(),
        )

        smtp.send_message(msg=message)


@shared_task(
    bind=True,
    name="backend.services.tasks.sync_moex_market_data",
    max_retries=3,
)
def sync_moex_market_data(task) -> dict[str, int]:
    try:
        securities_count, history_count = sync_market_data()
    except Exception as exc:
        raise task.retry(exc=exc, countdown=300) from exc

    return {
        "securities": securities_count,
        "market_rows": history_count,
    }