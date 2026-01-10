-- 添加报告URL字段到需求分析和缺陷分析表
-- 执行时间: 2026-01-09

-- 添加需求分析表的 report_url 字段
ALTER TABLE test_requirement_analysis 
ADD COLUMN report_url VARCHAR(500) NULL COMMENT '分析报告URL' AFTER mindmap_url;

-- 添加缺陷分析表的 report_url 字段
ALTER TABLE test_defect_analysis 
ADD COLUMN report_url VARCHAR(500) NULL COMMENT '分析报告URL' AFTER mindmap_url;

-- 添加索引（可选，如果需要根据报告URL查询）
-- CREATE INDEX idx_requirement_analysis_report_url ON test_requirement_analysis(report_url);
-- CREATE INDEX idx_defect_analysis_report_url ON test_defect_analysis(report_url);

