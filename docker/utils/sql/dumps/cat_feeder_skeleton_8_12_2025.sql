/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.13-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: cat_feeder
-- ------------------------------------------------------
-- Server version	8.4.7

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `cat_feeder`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `cat_feeder` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `cat_feeder`;

--
-- Table structure for table `Beacon`
--

DROP TABLE IF EXISTS `Beacon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Beacon` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'The primary key of the table.',
  `owner` bigint unsigned NOT NULL COMMENT 'The id of the account that owns the beacon.',
  `mac` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'The mac address of the beacon.',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'friendly name' COMMENT 'The name of the beacon to help the human identify it so that it makes more sense.',
  `creation_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'The date at which the line was added.',
  `edit_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'The current time at which the line was edited.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `beacon_unique` (`mac`),
  UNIQUE KEY `beacon_name_unique` (`name`),
  KEY `beacon_Users_FK` (`owner`),
  CONSTRAINT `beacon_Users_FK` FOREIGN KEY (`owner`) REFERENCES `Users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='The beacons that are detected by the feeders.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Beacon`
--

LOCK TABLES `Beacon` WRITE;
/*!40000 ALTER TABLE `Beacon` DISABLE KEYS */;
/*!40000 ALTER TABLE `Beacon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Feeder`
--

DROP TABLE IF EXISTS `Feeder`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Feeder` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'The primary key of the table',
  `owner` bigint unsigned NOT NULL COMMENT 'The id of the account that owns the feeder.',
  `latitude` decimal(10,8) NOT NULL COMMENT 'The latitude coordinate for the feeder.',
  `longitude` decimal(11,8) NOT NULL COMMENT 'This is the longitude used for the feeder.',
  `city_locality` varchar(255) NOT NULL COMMENT 'The human readable name of the cirty/locality.',
  `country` varchar(255) NOT NULL COMMENT 'The country name of the location of the feeder.',
  `mac` varchar(20) NOT NULL COMMENT 'The mac address of the feeder.',
  `name` varchar(255) NOT NULL DEFAULT 'friendly name' COMMENT 'The name of the feeder to help the human identify it so that it makes more sense.',
  `creation_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'The date at which the line was added.',
  `edit_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'The current time at which the line was edited.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `Feeder_mac_UNIQUE` (`mac`),
  UNIQUE KEY `Feeder_name_UNIQUE` (`name`),
  KEY `Feeder_Users_FK` (`owner`),
  CONSTRAINT `Feeder_Users_FK` FOREIGN KEY (`owner`) REFERENCES `Users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='The feeder''s properties.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Feeder`
--

LOCK TABLES `Feeder` WRITE;
/*!40000 ALTER TABLE `Feeder` DISABLE KEYS */;
/*!40000 ALTER TABLE `Feeder` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Location_history`
--

DROP TABLE IF EXISTS `Location_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Location_history` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'The primary key of the table.',
  `beacon` bigint unsigned NOT NULL COMMENT 'The id of the beacon.',
  `feeder` bigint unsigned NOT NULL COMMENT 'The id of the feeder that was used.',
  `creation_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'The date at which the line was added.',
  `edit_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'The current time at which the line was edited.',
  PRIMARY KEY (`id`),
  KEY `Location_history_Beacon_FK` (`feeder`),
  CONSTRAINT `Location_history_Beacon_FK` FOREIGN KEY (`feeder`) REFERENCES `Beacon` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Location_history_Feeder_FK` FOREIGN KEY (`id`) REFERENCES `Feeder` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='The different locations the beacon was found at.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Location_history`
--

LOCK TABLES `Location_history` WRITE;
/*!40000 ALTER TABLE `Location_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `Location_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Pet`
--

DROP TABLE IF EXISTS `Pet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Pet` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'The primary key of the table.',
  `beacon` bigint unsigned NOT NULL COMMENT 'The id of the beacon assigned to the pet.',
  `name` varchar(255) NOT NULL DEFAULT 'Pet name' COMMENT 'The name of the pet.',
  `food_eaten` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'The quantity of food the animal has eaten.',
  `food_max` bigint unsigned NOT NULL DEFAULT '100' COMMENT 'The maximum amount of food the pet is allowed to eat.',
  `food_reset` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'The time (in DATETIME) when to reset the food counter.',
  `time_reset_hours` bigint unsigned NOT NULL DEFAULT '24' COMMENT 'The time (hours) used to track the when to reset the food counter.',
  `time_reset_minutes` bigint unsigned NOT NULL DEFAULT '0' COMMENT 'The time (minutes) used to track the when to reset the food counter.',
  `creation_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'The date at which the line was added.',
  `edit_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'The current time at which the line was edited.',
  PRIMARY KEY (`id`),
  KEY `Pet_Beacon_FK` (`beacon`),
  CONSTRAINT `Pet_Beacon_FK` FOREIGN KEY (`beacon`) REFERENCES `Beacon` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='The data relating to the animal to which the beacon is attached.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Pet`
--

LOCK TABLES `Pet` WRITE;
/*!40000 ALTER TABLE `Pet` DISABLE KEYS */;
/*!40000 ALTER TABLE `Pet` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Users` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'This is the primary key for the table',
  `username` varchar(1000) NOT NULL DEFAULT 'user' COMMENT 'The username of the account',
  `email` varchar(255) NOT NULL COMMENT 'The e-mail used for the account',
  `creation_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'The date at which the user colum was created.',
  `edit_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'The date at which the line was edited.',
  PRIMARY KEY (`id`),
  UNIQUE KEY `Users_email_UNIQUE` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='This is the table that will contain the names and accounts of the users for the server.';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Users`
--

LOCK TABLES `Users` WRITE;
/*!40000 ALTER TABLE `Users` DISABLE KEYS */;
/*!40000 ALTER TABLE `Users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-08  2:11:05
