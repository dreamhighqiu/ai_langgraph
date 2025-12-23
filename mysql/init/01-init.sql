-- MySQL 初始化脚本
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS ai_langgraph CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_langgraph;

-- 创建示例表
CREATE TABLE IF NOT EXISTS `system_config` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `config_key` VARCHAR(100) NOT NULL UNIQUE,
  `config_value` TEXT,
  `description` VARCHAR(255),
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入初始配置
INSERT INTO `system_config` (`config_key`, `config_value`, `description`) VALUES
('app_name', 'AI LangGraph', '应用名称'),
('app_version', '1.0.0', '应用版本'),
('initialized_at', NOW(), '初始化时间')
ON DUPLICATE KEY UPDATE config_value=VALUES(config_value);

-- 创建用户表示例
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(50) NOT NULL UNIQUE,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_username (username),
  INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建对话历史表
CREATE TABLE IF NOT EXISTS `chat_history` (
  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
  `session_id` VARCHAR(100) NOT NULL,
  `user_id` BIGINT,
  `role` ENUM('user', 'assistant', 'system') NOT NULL,
  `content` TEXT NOT NULL,
  `metadata` JSON,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_session_id (session_id),
  INDEX idx_user_id (user_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 授权
GRANT ALL PRIVILEGES ON ai_langgraph.* TO 'aiuser'@'%';
FLUSH PRIVILEGES;

SELECT 'MySQL 数据库初始化完成！' AS message;

