Waves.Youhu.Metadata
简单HTTP文件下载服务。

接口：
- GET /files/resource/{category}/{path}
- GET /files/map/{path}

安全：
- 速率限制（每IP窗口限次）、路径长度与段数限制、连续404自动封禁。
