FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN python -m compileall -q main.py backend && python ML/train_recommendation_model.py

RUN addgroup --system app && adduser --system --ingroup app app \
	&& chown -R app:app /app

USER app

CMD ["sh", "-c", "python ML/train_recommendation_model.py && uvicorn main:app --host 0.0.0.0 --port 8000"]