CREATE DATABASE  IF NOT EXISTS `inventory_database` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `inventory_database`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: inventory_database
-- ------------------------------------------------------
-- Server version	9.3.0-commercial

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employees` (
  `employee_id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `user_account` int DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL,
  PRIMARY KEY (`employee_id`),
  KEY `user_account_idx` (`user_account`),
  CONSTRAINT `user_account` FOREIGN KEY (`user_account`) REFERENCES `user_accounts` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (1,'Seth Owen',NULL,'2025-03-11 10:24:56'),(2,'Sona Lona',NULL,'2025-03-13 15:03:05'),(3,'Dave Piattos',NULL,'2025-03-13 15:25:27'),(4,'Usman Powell',NULL,'2025-03-17 13:42:52'),(5,'Aadam Black',NULL,'2025-03-17 13:42:59'),(6,'Lee Crawford',NULL,'2025-03-17 13:43:07'),(7,'Oliver Buchanan',NULL,'2025-03-17 13:43:14'),(8,'Bailey Harvey',NULL,'2025-03-17 13:43:21'),(9,'Khalid Shaw',NULL,'2025-03-17 13:43:27'),(10,'Hugo Long',NULL,'2025-03-17 13:43:34'),(11,'Marcel Marsh',NULL,'2025-03-17 13:43:40'),(12,'Jeffrey Humphrey',NULL,'2025-03-17 13:43:45'),(13,'Alex Pratt',NULL,'2025-03-17 13:43:51'),(14,'Beth Silva',NULL,'2025-03-17 13:44:10'),(15,'Christine Russell',NULL,'2025-03-17 13:44:17'),(16,'Hollie Blankenship',NULL,'2025-03-17 13:46:02'),(17,'Monica Humphrey',NULL,'2025-03-17 13:46:07'),(18,'Nettie Peck',NULL,'2025-03-17 13:46:12'),(19,'Brianna Willis',NULL,'2025-03-17 13:46:17'),(20,'Elise Pratt',NULL,'2025-03-17 13:46:22'),(21,'Veronica England',NULL,'2025-03-17 13:46:26'),(22,'Mason Decker',NULL,'2025-03-17 13:46:31'),(23,'Emily Fry',NULL,'2025-03-17 13:46:35'),(24,'test',NULL,'2025-03-20 12:21:06');
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_assignment_history`
--

DROP TABLE IF EXISTS `item_assignment_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_assignment_history` (
  `history_id` int NOT NULL AUTO_INCREMENT,
  `item_id` varchar(32) NOT NULL,
  `employee_id` int DEFAULT NULL,
  `assigned_date` datetime NOT NULL,
  `removed_date` datetime DEFAULT NULL,
  PRIMARY KEY (`history_id`),
  KEY `item_assignment_history_ibfk_2` (`employee_id`),
  KEY `item_assignment_history_ibfk_1` (`item_id`),
  CONSTRAINT `item_assignment_history_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`item_id`),
  CONSTRAINT `item_assignment_history_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`employee_id`) ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_assignment_history`
--

LOCK TABLES `item_assignment_history` WRITE;
/*!40000 ALTER TABLE `item_assignment_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `item_assignment_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `item_id` varchar(12) NOT NULL,
  `serial_number` varchar(45) DEFAULT NULL,
  `item_name` varchar(45) NOT NULL,
  `category` varchar(45) NOT NULL,
  `description` varchar(150) NOT NULL,
  `comment` varchar(75) NOT NULL,
  `employee` int DEFAULT NULL,
  `department` varchar(45) DEFAULT NULL,
  `status` varchar(45) NOT NULL,
  `last_updated` datetime DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  UNIQUE KEY `serial_number_UNIQUE` (`serial_number`),
  KEY `employee_idx` (`employee`),
  CONSTRAINT `employee` FOREIGN KEY (`employee`) REFERENCES `employees` (`employee_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES ('MLQU-0000001','MKDK99','AVR','Computer','Computer ','test',NULL,'MIS','active','2025-05-19 12:11:58'),('MLQU-0000002','234234','Monitor','','Acer 768p','',3,'Department 6','','2025-03-17 10:33:37'),('MLQU-0000003','asd','ad','','asda','',4,'Department 4','','2025-03-17 13:47:07'),('MLQU-0000004','ad23232','Keyboard','','Full - size','',2,'Department 2','','2025-03-17 15:49:13'),('MLQU-0000005','LMNOP123','Mouse','','A4tech','',1,'Department 5','','2025-03-17 15:48:51'),('MLQU-0000006','ABCD123','Speaker','','JBL - Large','',7,'Department 3','','2025-03-17 15:48:07'),('MLQU-0000007','LMNOP02','Chair','Category 2','Red foam','',3,'Department 2','','2025-03-31 15:28:22');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_accounts`
--

DROP TABLE IF EXISTS `user_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_accounts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `password` varchar(255) NOT NULL,
  `account_type` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_accounts`
--

LOCK TABLES `user_accounts` WRITE;
/*!40000 ALTER TABLE `user_accounts` DISABLE KEYS */;
INSERT INTO `user_accounts` VALUES (1,'admin','scrypt:32768:8:1$DattLRJFgJxAx2Rb$0373269bbeff179a91bde24fd84a612be493a50e0ff4bec3449ad0490253e49e5d09da6507d09111e98ba72c6cb2e576a1d9437612d67b81da3b2e310157e12f','admin'),(2,'user','scrypt:32768:8:1$W1Qi7AoGzDsQd8hL$409ad1d61c84fe2133f54ade3c28296edce0737278d34e2b848b65a5f2437800bd5486060beacad8741bb6a47883b5a791ea38f6d923b2876e9d67fef22529cb','user');
/*!40000 ALTER TABLE `user_accounts` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-19 12:32:29
