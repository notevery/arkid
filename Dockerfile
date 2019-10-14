FROM python:3.6 as base
EXPOSE 80
WORKDIR /var/oneid

FROM base as run_lint
ADD requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
ADD . .
ARG base_commit_id=""
RUN pre-commit install \
    && make BASE_COMMIT_ID=${base_commit_id} lint

FROM base as build_deps
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM build_deps as run_test
ADD . .
RUN make test

FROM build_deps as build
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim supervisor gettext \
    && pip install uwsgi
ADD . .
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
RUN \
    sed -i "s|LANGUAGE_CODE = 'zh_hans'|LANGUAGE_CODE = 'zh-hans'|g" oneid/settings.py && \
    python manage.py compilemessages && \
    sed -i "s|LANGUAGE_CODE = 'zh-hans'|LANGUAGE_CODE = 'zh_hans'|g" oneid/settings.py
CMD python manage.py migrate && supervisord
