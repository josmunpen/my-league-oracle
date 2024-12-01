FROM python:3.11.4

WORKDIR /code

COPY ./requirements_backend.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./backend /code/backend

# RUN ls -la /code
# RUN ls -la /code/backend
# RUN ls -la /code/backend/models/

CMD ["fastapi", "run", "backend/main.py", "--port", "8000"]