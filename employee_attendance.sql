-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 04, 2025 at 07:12 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `employee_attendance`
--

-- --------------------------------------------------------

--
-- Table structure for table `alembic_version`
--

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('f171afe2db72');

-- --------------------------------------------------------

--
-- Table structure for table `attendance`
--

CREATE TABLE `attendance` (
  `attendance_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `attendance_date` date NOT NULL,
  `check_in_time` timestamp NULL DEFAULT NULL,
  `check_out_time` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `attendance`
--

INSERT INTO `attendance` (`attendance_id`, `user_id`, `attendance_date`, `check_in_time`, `check_out_time`) VALUES
(1, 14, '2025-01-27', '2025-01-27 15:59:50', NULL),
(2, 14, '2025-01-28', '2025-01-27 16:01:57', NULL),
(4, 14, '2025-01-30', '2025-01-29 17:59:14', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `inventory`
--

CREATE TABLE `inventory` (
  `item_id` int(11) NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `quantity` int(11) NOT NULL,
  `price` float NOT NULL,
  `added_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `qr__codes`
--

CREATE TABLE `qr__codes` (
  `qr_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `generated_at` timestamp NULL DEFAULT NULL,
  `qr_code_path` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `qr__codes`
--

INSERT INTO `qr__codes` (`qr_id`, `user_id`, `generated_at`, `qr_code_path`) VALUES
(3, 14, '2025-01-28 16:02:14', 'app/static/qr_codes/user_14.png'),
(4, 14, '2025-01-29 15:12:45', 'app/static/qr_codes/user_14.png'),
(5, 14, '2025-01-29 16:23:15', 'app/static/qr_codes/user_14.png'),
(6, 14, '2025-01-29 18:00:11', 'app/static/qr_codes/user_14.png'),
(7, 14, '2025-01-30 08:21:57', 'app/static/qr_codes/user_14.png'),
(8, 14, '2025-01-30 08:22:07', 'app/static/qr_codes/user_14.png'),
(9, 14, '2025-01-30 08:33:03', 'app/static/qr_codes/user_14.png'),
(10, 14, '2025-01-30 09:54:43', 'app/static/qr_codes/user_14.png'),
(11, 14, '2025-01-30 10:17:07', 'app/static/qr_codes/user_14.png'),
(12, 14, '2025-01-30 10:17:46', 'app/static/qr_codes/user_14.png'),
(13, 14, '2025-02-03 10:02:52', 'app/static/qr_codes/user_14.png'),
(14, 14, '2025-02-03 10:20:00', 'app/static/qr_codes/user_14.png'),
(15, 14, '2025-02-03 10:20:05', 'app/static/qr_codes/user_14.png'),
(16, 14, '2025-02-03 10:20:10', 'app/static/qr_codes/user_14.png'),
(17, 14, '2025-02-03 11:00:39', 'app/static/qr_codes/user_14.png'),
(18, 14, '2025-02-03 11:02:02', 'app/static/qr_codes/user_14.png'),
(19, 14, '2025-02-03 11:03:45', 'app/static/qr_codes/user_14.png'),
(20, 14, '2025-02-03 11:04:10', 'app/static/qr_codes/user_14.png'),
(21, 14, '2025-02-03 11:04:28', 'app/static/qr_codes/user_14.png'),
(22, 14, '2025-02-03 11:05:09', 'app/static/qr_codes/user_14.png'),
(23, 14, '2025-02-03 11:05:18', 'app/static/qr_codes/user_14.png'),
(24, 14, '2025-02-03 11:05:30', 'app/static/qr_codes/user_14.png'),
(25, 14, '2025-02-03 11:06:18', 'app/static/qr_codes/user_14.png'),
(26, 14, '2025-02-03 11:23:56', 'app/static/qr_codes/user_14.png'),
(27, 14, '2025-02-03 11:25:09', 'app/static/qr_codes/user_14.png'),
(28, 14, '2025-02-03 11:25:40', 'app/static/qr_codes/user_14.png'),
(29, 14, '2025-02-03 11:27:45', 'app/static/qr_codes/user_14.png'),
(30, 14, '2025-02-03 11:27:55', 'app/static/qr_codes/user_14.png'),
(31, 14, '2025-02-03 11:31:19', 'app/static/qr_codes/user_14.png'),
(32, 14, '2025-02-03 11:31:37', 'app/static/qr_codes/user_14.png'),
(33, 14, '2025-02-03 11:32:05', 'app/static/qr_codes/user_14.png'),
(34, 14, '2025-02-03 11:32:34', 'app/static/qr_codes/user_14.png'),
(35, 14, '2025-02-03 11:33:05', 'app/static/qr_codes/user_14.png'),
(36, 14, '2025-02-03 11:33:30', 'app/static/qr_codes/user_14.png'),
(37, 14, '2025-02-03 11:33:59', 'app/static/qr_codes/user_14.png'),
(38, 14, '2025-02-03 11:34:09', 'app/static/qr_codes/user_14.png'),
(39, 14, '2025-02-03 11:34:37', 'app/static/qr_codes/user_14.png'),
(40, 14, '2025-02-03 11:34:49', 'app/static/qr_codes/user_14.png'),
(41, 14, '2025-02-03 11:35:08', 'app/static/qr_codes/user_14.png'),
(42, 14, '2025-02-03 11:35:17', 'app/static/qr_codes/user_14.png'),
(43, 15, '2025-02-03 11:35:17', 'app/static/qr_codes/user_15.png'),
(44, 14, '2025-02-03 11:35:23', 'app/static/qr_codes/user_14.png'),
(45, 14, '2025-02-03 11:39:58', 'app/static/qr_codes/user_14.png'),
(46, 14, '2025-02-03 11:41:04', 'app/static/qr_codes/user_14.png'),
(47, 14, '2025-02-03 11:41:05', 'app/static/qr_codes/user_14.png'),
(48, 14, '2025-02-03 11:41:06', 'app/static/qr_codes/user_14.png'),
(49, 14, '2025-02-03 11:42:36', 'app/static/qr_codes/user_14.png'),
(50, 14, '2025-02-03 11:43:09', 'app/static/qr_codes/user_14.png'),
(51, 14, '2025-02-03 11:43:10', 'app/static/qr_codes/user_14.png'),
(52, 16, '2025-02-03 11:45:42', 'app/static/qr_codes/user_16.png'),
(53, 19, '2025-02-03 11:46:19', 'app/static/qr_codes/user_19.png'),
(54, 14, '2025-02-03 11:46:19', 'app/static/qr_codes/user_14.png'),
(55, 14, '2025-02-03 11:47:01', 'app/static/qr_codes/user_14.png'),
(56, 14, '2025-02-03 11:47:02', 'app/static/qr_codes/user_14.png'),
(57, 14, '2025-02-03 11:47:39', 'app/static/qr_codes/user_14.png'),
(58, 14, '2025-02-03 11:48:16', 'app/static/qr_codes/user_14.png'),
(59, 14, '2025-02-03 11:48:29', 'app/static/qr_codes/user_14.png'),
(60, 14, '2025-02-03 11:48:30', 'app/static/qr_codes/user_14.png'),
(61, 14, '2025-02-03 11:48:33', 'app/static/qr_codes/user_14.png'),
(62, 14, '2025-02-03 11:48:39', 'app/static/qr_codes/user_14.png'),
(63, 14, '2025-02-03 11:48:46', 'app/static/qr_codes/user_14.png'),
(64, 14, '2025-02-03 11:51:38', 'app/static/qr_codes/user_14.png'),
(65, 14, '2025-02-03 11:51:55', 'app/static/qr_codes/user_14.png'),
(66, 14, '2025-02-03 11:52:49', 'app/static/qr_codes/user_14.png'),
(67, 14, '2025-02-03 11:53:46', 'app/static/qr_codes/user_14.png'),
(68, 14, '2025-02-03 11:54:35', 'app/static/qr_codes/user_14.png'),
(69, 14, '2025-02-03 11:54:50', 'app/static/qr_codes/user_14.png'),
(70, 14, '2025-02-03 11:55:40', 'app/static/qr_codes/user_14.png'),
(71, 14, '2025-02-03 11:56:23', 'app/static/qr_codes/user_14.png'),
(72, 14, '2025-02-03 11:57:09', 'app/static/qr_codes/user_14.png'),
(73, 14, '2025-02-03 11:57:22', 'app/static/qr_codes/user_14.png'),
(74, 14, '2025-02-03 11:58:30', 'app/static/qr_codes/user_14.png'),
(75, 14, '2025-02-03 12:21:55', 'app/static/qr_codes/user_14.png'),
(76, 14, '2025-02-03 12:22:38', 'app/static/qr_codes/user_14.png'),
(77, 14, '2025-02-03 12:23:02', 'app/static/qr_codes/user_14.png'),
(78, 14, '2025-02-03 12:23:50', 'app/static/qr_codes/user_14.png'),
(79, 14, '2025-02-03 12:24:02', 'app/static/qr_codes/user_14.png'),
(80, 14, '2025-02-03 12:24:55', 'app/static/qr_codes/user_14.png'),
(81, 14, '2025-02-03 12:25:00', 'app/static/qr_codes/user_14.png'),
(82, 14, '2025-02-03 12:25:11', 'app/static/qr_codes/user_14.png'),
(83, 14, '2025-02-03 12:25:50', 'app/static/qr_codes/user_14.png'),
(84, 14, '2025-02-03 12:26:08', 'app/static/qr_codes/user_14.png'),
(85, 14, '2025-02-03 12:26:47', 'app/static/qr_codes/user_14.png'),
(86, 14, '2025-02-03 12:26:53', 'app/static/qr_codes/user_14.png'),
(87, 14, '2025-02-03 13:26:49', 'app/static/qr_codes/user_14.png'),
(88, 14, '2025-02-03 13:26:52', 'app/static/qr_codes/user_14.png');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role` enum('Admin','Employee') NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `firstname` varchar(100) NOT NULL,
  `middlename` varchar(100) DEFAULT NULL,
  `lastname` varchar(100) NOT NULL,
  `suffix` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password_hash`, `email`, `role`, `created_at`, `updated_at`, `firstname`, `middlename`, `lastname`, `suffix`) VALUES
(1, 'admin', 'scrypt:32768:8:1$xHoYHhSx3hLqLDst$cddbc37d8dad4670b748cfac02f8f8fdcbbc1b3ddc70885025eb310bed080e6ae919624d9701c55742bf3cd6733ecebafe2c8ffce25b6383cb441812a8de5686', 'admin@gmail.com', 'Admin', '2025-01-27 07:29:35', '2025-01-27 07:29:35', 'stephen', 'gonzales', 'aguilar', NULL),
(11, 'username', 'scrypt:32768:8:1$kiCwtS4JD2wvva0b$b0fd1bb0e1109830ec65887318d730f08bcbce524ee381c0a3bafc9d9faaff79332f770f4bc202e8017df2121294874b285f92043de86f08dd61c1a7e2f479cc', 'username@domain.com', 'Employee', '2025-01-27 11:01:37', '2025-01-27 11:01:37', 'asdf', 'asdf', 'asdf', 'asdf'),
(14, 'employee', 'scrypt:32768:8:1$T59EbjsHF2zRhisL$92344098577010a6aae11bd7897f6b1e0bb57c6db4dd1c26a8b872fd7893c9989795bd0eb99686b034224f803b433b1710df49df533d058dafdca3ad9db0c507', 'employee@gmail.com', 'Employee', '2025-01-27 11:22:42', '2025-01-27 11:22:42', 'employee', 'asd', 'po', 'asd'),
(15, '', 'scrypt:32768:8:1$aVzUlnRsHyO5jVYs$9eece1729abe2a2b2ae2a2ff7e9747510714f8e55143499d8ea440ac1db4ab719f1739f9130c6bd6ec06181b99786403008a90ca44ab9a4944c9b24f9012aefc', '', 'Employee', '2025-02-03 11:35:17', '2025-02-03 11:35:17', '', '', '', ''),
(16, 'asd', 'scrypt:32768:8:1$7CUkyecT6O7HxdtN$c6c7d5ef94c0873d7d444dc7cca5b8a343579e5eed0b1ed236300d586e42011cfdabcb8bdd53c91ab9adc2b495e837670ee34babf4e1bf7f2c805f246d93e22c', 'asdasd@gmail.com', 'Employee', '2025-02-03 11:45:42', '2025-02-03 11:45:42', 'asd', 'asd', 'asd', 'asd'),
(19, 'asda', 'scrypt:32768:8:1$3ld0bx6ceisWt3a6$3e7c9796c92036cc3aa5bc3ee844a255ef305816de83ae7bb961884d67409cd35315777d2854adf308798d305f5d2d92bf06552bc49bb2f2f984af594dca4e78', 'asdasd@gmail.com', 'Employee', '2025-02-03 11:46:19', '2025-02-03 11:46:19', 'asda', 'asd', 'asd', 'asdaa');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `alembic_version`
--
ALTER TABLE `alembic_version`
  ADD PRIMARY KEY (`version_num`);

--
-- Indexes for table `attendance`
--
ALTER TABLE `attendance`
  ADD PRIMARY KEY (`attendance_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `inventory`
--
ALTER TABLE `inventory`
  ADD PRIMARY KEY (`item_id`);

--
-- Indexes for table `qr__codes`
--
ALTER TABLE `qr__codes`
  ADD PRIMARY KEY (`qr_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `attendance`
  MODIFY `attendance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `inventory`
--
ALTER TABLE `inventory`
  MODIFY `item_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `qr__codes`
--
ALTER TABLE `qr__codes`
  MODIFY `qr_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=89;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `attendance`
--
ALTER TABLE `attendance`
  ADD CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `qr__codes`
--
ALTER TABLE `qr__codes`
  ADD CONSTRAINT `qr__codes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
