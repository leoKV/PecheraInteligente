CREATE DATABASE ddi01;

USE ddi01;

CREATE TABLE users(
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  login VARCHAR(250),
  password VARCHAR(550),
  record_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sensors_types(
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  name VARCHAR(250),
  record_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sensors(
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  name VARCHAR(250),
  sensor_type INT,
  record_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(sensor_type)REFERENCES sensors_types(id)
);

CREATE TABLE sensor_data(
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  sensor INT,
  user INT,
  value INT,
  record_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(sensor)REFERENCES sensors(id),
  FOREIGN KEY(user)REFERENCES users(id)
);

INSERT INTO users(login,password)VALUES('kvaldez','kv123');

INSERT INTO sensors_types(name)VALUES('Digital');
INSERT INTO sensors_types(name)VALUES('Analogico');
INSERT INTO sensors_types(name)VALUES('Mixto');

INSERT INTO sensors(name,sensor_type)VALUES('MQ5',3);
INSERT INTO sensors(name,sensor_type)VALUES('Sensor de lluvia',3);
INSERT INTO sensors(name,sensor_type)VALUES('ds18b20',1);
INSERT INTO sensors(name,sensor_type)VALUES('Fotoresistencia',2);





