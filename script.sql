DROP DATABASE IF EXISTS familytreedb;
CREATE DATABASE familytreedb;
DROP USER IF EXISTS 'familytreedefault'@'localhost';
CREATE USER 'familytreedefault'@'localhost' IDENTIFIED BY 'familytreedefaultpwd';
GRANT ALL PRIVILEGES ON *.* TO 'familytreedefault'@'localhost' IDENTIFIED BY 'familytreedefaultpwd' WITH GRANT OPTION;
FLUSH PRIVILEGES;
