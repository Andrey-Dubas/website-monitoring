CREATE DATABASE website_monitoring;
\connect website_monitoring;

CREATE SCHEMA IF NOT EXISTS app_data AUTHORIZATION "adubas";

CREATE TABLE app_data.targets (
	url VARCHAR (255) PRIMARY KEY,
	created_at TIMESTAMP NOT NULL default current_timestamp,
	updated_at TIMESTAMP NOT NULL default current_timestamp
);

CREATE TABLE app_data.requests (
	url VARCHAR (255) NOT NULL,
	status_code INT,
	found_pattern BOOL,
	is_reached BOOL NOT NULL,
	created_at TIMESTAMP NOT NULL default current_timestamp,
	CONSTRAINT fk_url
      FOREIGN KEY(url) 
        REFERENCES app_data.targets(url)
);