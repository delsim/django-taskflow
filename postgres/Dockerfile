ARG DOCKER_VAR_POSTGRES
FROM postgres:$DOCKER_VAR_POSTGRES
WORKDIR /usr/src/app
#
ENV POSTGRES_PASSWORD dtftest
ENV POSTGRES_USER     dtftest
ENV POSTGRES_DB       dtftest
#
ENV PGDATA            /var/lib/postgresql/data/pgdata
#
