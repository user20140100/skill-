# POOL：线程池、连接池与排队

规则 ID：POOL-01 持续饱和；POOL-02 等待/拒绝；POOL-03 无界资源及隔离缺失。

发现源码和生效配置里的业务线程池、Web/RPC executor、定时池、异步任务池，以及 JDBC、HTTP、RPC、Redis 等连接池。记录池名称、实例、容量/最大值、队列类型、等待超时和拒绝策略。默认配置不等于线上生效配置。

运行态优先使用 `ccloud-cli observe metrics-list` → `metrics` 及 `observe logs/logs-count` 核查 active/max、queue/capacity、pending/waiters、acquire latency/timeouts、rejected、连接创建/泄漏检测；通过 `app comprehensive` 核查实际返回的相关配置，结合源码确认池模型。没有专用池诊断 action 不代表指标与日志查询不支持，但目录未暴露的池指标不能猜 ID。指标缺失只能标未验证。不要只采一次 active=max 就认定长期打满。

## 判定

- 饱和需要持续时间、峰值与等待/拒绝或接口影响证据；瞬时利用率高但无等待不一定异常。
- 线程池 maxThreads、实际 poolSize、activeThreads 含义分开；无界队列容量不能直接计算饱和比例。
- JDBC active 接近 max 与 pending/获取超时共同判断；HTTP/RPC/Redis 池按客户端真实模型解释，不套 JDBC 指标。
- 检查共用池导致慢任务拖垮关键任务、CallerRuns 把阻塞传回请求线程、嵌套提交后等待同池结果、长事务持有连接、连接未关闭、泄漏和无界 future/队列。
- 拒绝日志缺失不证明无拒绝；取样堆栈只在已有可用证据或授权诊断下读取。

建议结合到达率与服务时间、下游容量做预算。平均并发≈到达率×平均服务时间仅用于相同稳定窗口估算，不能直接拿 p99 代入得出精确容量。不要把扩大线程池/连接池作为默认修复，可能放大数据库和依赖压力。

验收：代表峰值下等待时间与拒绝率满足服务目标、队列有界且可恢复、连接无持续泄漏、下游容量允许；同步超时与资源释放链一致。
