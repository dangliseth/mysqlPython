CREATE DATABASE  IF NOT EXISTS `inventory_database` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `inventory_database`;
-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: inventory_database
-- ------------------------------------------------------
-- Server version	8.0.41

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
  `last_updated` datetime DEFAULT NULL,
  PRIMARY KEY (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` VALUES (1,'Seth Owen','2025-03-11 10:24:56'),(2,'Sona Lona','2025-03-13 15:03:05'),(3,'Dave Piattos','2025-03-13 15:25:27'),(4,'Usman Powell','2025-03-17 13:42:52'),(5,'Aadam Black','2025-03-17 13:42:59'),(6,'Lee Crawford','2025-03-17 13:43:07'),(7,'Oliver Buchanan','2025-03-17 13:43:14'),(8,'Bailey Harvey','2025-03-17 13:43:21'),(9,'Khalid Shaw','2025-03-17 13:43:27'),(10,'Hugo Long','2025-03-17 13:43:34'),(11,'Marcel Marsh','2025-03-17 13:43:40'),(12,'Jeffrey Humphrey','2025-03-17 13:43:45'),(13,'Alex Pratt','2025-03-17 13:43:51'),(14,'Beth Silva','2025-03-17 13:44:10'),(15,'Christine Russell','2025-03-17 13:44:17'),(16,'Hollie Blankenship','2025-03-17 13:46:02'),(17,'Monica Humphrey','2025-03-17 13:46:07'),(18,'Nettie Peck','2025-03-17 13:46:12'),(19,'Brianna Willis','2025-03-17 13:46:17'),(20,'Elise Pratt','2025-03-17 13:46:22'),(21,'Veronica England','2025-03-17 13:46:26'),(22,'Mason Decker','2025-03-17 13:46:31'),(23,'Emily Fry','2025-03-17 13:46:35'),(24,'test','2025-03-20 12:21:06');
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
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
  `description` varchar(150) DEFAULT NULL,
  `employee` int DEFAULT NULL,
  `department` varchar(45) DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  UNIQUE KEY `serial_number_UNIQUE` (`serial_number`),
  KEY `employee_idx` (`employee`),
  CONSTRAINT `employee` FOREIGN KEY (`employee`) REFERENCES `employees` (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES ('MLQU-0000001','MKDK99','AVR','','Computer ',1,'Department 1','2025-03-14 10:59:09'),('MLQU-0000002','234234','Monitor','','Acer 768p',3,'Department 6','2025-03-17 10:33:37'),('MLQU-0000003','asd','ad','','asda',4,'Department 4','2025-03-17 13:47:07'),('MLQU-0000004','ad23232','Keyboard','','Full - size',2,'Department 2','2025-03-17 15:49:13'),('MLQU-0000005','LMNOP123','Mouse','','A4tech',1,'Department 5','2025-03-17 15:48:51'),('MLQU-0000006','ABCD123','Speaker','','JBL - Large',7,'Department 3','2025-03-17 15:48:07'),('MLQU-0000007','LMNOP02','Chair','Category 2','Red foam',3,'Department 2','2025-03-31 15:28:22');
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
  `password` varchar(45) DEFAULT NULL,
  `account_type` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username_UNIQUE` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_accounts`
--

LOCK TABLES `user_accounts` WRITE;
/*!40000 ALTER TABLE `user_accounts` DISABLE KEYS */;
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

-- Dump completed on 2025-04-07 15:49:03
