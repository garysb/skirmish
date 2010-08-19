-- Skirmish database core
SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT=0;
START TRANSACTION;

-- --------------------------------------------------------
-- Table structure for table `Avatars`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Avatars` (
  `a_id` INT(8) unsigned NOT NULL AUTO_INCREMENT,
  `u_id` INT(8) unsigned NOT NULL COMMENT 'User',
  `a_name` VARCHAR(10) NOT NULL,
  `a_type` VARCHAR(10) NOT NULL,
  PRIMARY KEY (`a_id`),
  KEY `u_id` (`u_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COMMENT='Users list of avatars' AUTO_INCREMENT=3 ;

-- --------------------------------------------------------
-- Table structure for table `Users`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `Users` (
  `u_id` INT(8) unsigned NOT NULL AUTO_INCREMENT,
  `u_username` CHAR(64) NOT NULL,
  `u_password` CHAR(32) NOT NULL,
  `u_forename` VARCHAR(256) NOT NULL,
  `u_surname` VARCHAR(256) NOT NULL,
  `u_expiry` TIMESTAMP NULL DEFAULT NULL,
  `u_disabled` TINYINT(1) NOT NULL DEFAULT '0',
  `u_banned` TINYINT(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`u_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------
COMMIT;

