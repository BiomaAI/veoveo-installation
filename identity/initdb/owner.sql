-- The application owns only its database; it is not the PostgreSQL superuser.
\getenv owner_password KEYCLOAK_DATABASE_PASSWORD
CREATE ROLE keycloak LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD :'owner_password';
ALTER DATABASE keycloak OWNER TO keycloak;
\connect keycloak
ALTER SCHEMA public OWNER TO keycloak;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
