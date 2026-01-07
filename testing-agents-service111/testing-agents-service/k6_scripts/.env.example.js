# K6测试环境变量配置示例

# 访问令牌配置
ACCESS_TOKEN=your_actual_access_token_here

# 调试模式
DEBUG=false

# 性能测试配置
VUS=10
DURATION=30s

# 目标URL配置
BASE_URL=http://appserver.huice.com
HOME_PAGE_ENDPOINT=/cms/home/index

# 请求头配置
FECSHOP_CURRENCY=CNY
FECSHOP_LANG=zh

# 性能阈值配置
AVG_RESPONSE_TIME_THRESHOLD=100  # 平均响应时间阈值(ms)
P95_RESPONSE_TIME_THRESHOLD=200  # P95响应时间阈值(ms)
ERROR_RATE_THRESHOLD=0.01        # 错误率阈值(1%)
THROUGHPUT_THRESHOLD=50          # 吞吐量阈值(RPS)

# 思考时间配置
MIN_THINK_TIME=0.5  # 最小思考时间(秒)
MAX_THINK_TIME=1.0  # 最大思考时间(秒)

# 日志级别
LOG_LEVEL=info

# 输出配置
EXPORT_RESULTS=true
RESULTS_FILE=smoke_test_results.json
SUMMARY_FILE=smoke_test_summary.html