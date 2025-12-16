CREATE DATABASE `adguard` DEFAULT CHARACTER SET armscii8 COLLATE armscii8_general_ci;

USE `adguard`;

CREATE TABLE `querylog` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `time` datetime(6) NOT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  `client` varchar(64) DEFAULT NULL,
  `qtype` varchar(16) DEFAULT NULL,
  `answers` longtext DEFAULT NULL,
  `blocked` tinyint(1) DEFAULT NULL,
  `rule` varchar(255) DEFAULT NULL,
  `ruleid` smallint(5) UNSIGNED DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_event` (`time`,`hostname`,`client`,`qtype`)
) ENGINE=InnoDB;

CREATE TABLE `state` (
  `k` varchar(32) NOT NULL,
  `v` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`k`)
) ENGINE=InnoDB;

CREATE USER 'database-username'@'localhost' IDENTIFIED BY 'database-password';

GRANT ALL PRIVILEGES ON `adguard`.* TO 'database-username'@'localhost';
