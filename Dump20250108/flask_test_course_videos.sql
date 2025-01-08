-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: flask_test
-- ------------------------------------------------------
-- Server version	8.0.36

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
-- Table structure for table `course_videos`
--

DROP TABLE IF EXISTS `course_videos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course_videos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `course_id` varchar(45) NOT NULL,
  `video_name` varchar(255) NOT NULL,
  `video_url` varchar(255) NOT NULL,
  `thumbnail_url` varchar(255) DEFAULT NULL,
  `created_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course_videos`
--

LOCK TABLES `course_videos` WRITE;
/*!40000 ALTER TABLE `course_videos` DISABLE KEYS */;
INSERT INTO `course_videos` VALUES (23,'1450','CH1','static/videos\\114b1643-db1b-4259-ab04-f63b04a9ac6a_v1_test.mp4','static/thumbnails\\114b1643-db1b-4259-ab04-f63b04a9ac6a_v1_test.jpg','2025-01-07 12:57:29'),(24,'1450','CH1','static/videos\\f6e77f64-d4a7-4b45-9cbf-954f81c92668_v1_test.mp4','static/thumbnails\\f6e77f64-d4a7-4b45-9cbf-954f81c92668_v1_test.jpg','2025-01-07 13:03:01'),(25,'1450','CH1','static/videos\\v1_test.mp4','static/thumbnails\\v1_test.jpg','2025-01-07 13:09:16'),(26,'1450','CH1','static/videos\\v1_test.mp4','static/thumbnails\\v1_test.jpg','2025-01-07 13:10:45'),(27,'1450','CH1','static/videos\\v1_test.mp4','static/thumbnails\\v1_test.jpg','2025-01-07 13:17:29'),(28,'1450','CH2','static/videos\\v1_test.mp4','static/thumbnails\\v1_test.jpg','2025-01-07 14:36:23'),(29,'1450','CH1','static/videos\\v1_test.mp4','static/thumbnails\\v1_test.jpg','2025-01-07 15:19:38'),(30,'1450','CH1','static/videos\\v1_test.mp4','static/thumbnails\\v1_test.jpg','2025-01-07 15:34:09'),(31,'1450','CH1','static/videos\\v1_test.mp4','static/thumbnails\\v1_test.jpg','2025-01-07 15:45:12');
/*!40000 ALTER TABLE `course_videos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-08 10:12:49
