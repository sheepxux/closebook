# 计算机网络 期末复习范围（第 3、5 章）

## TCP 连接管理
- 三次握手：SYN → SYN+ACK → ACK。目的：双方确认彼此的发送和接收能力，并同步初始序列号（ISN）。
- 为什么不是两次：旧的重复 SYN 到达服务器时，两次握手会让服务器直接建立无用连接并浪费资源。
- 四次挥手：FIN → ACK → FIN → ACK；主动关闭方进入 TIME_WAIT，等待 2MSL。

## TCP 拥塞控制
- 慢启动：cwnd 从 1 MSS 开始，每个 RTT 翻倍，直到 ssthresh。
- 拥塞避免：超过 ssthresh 后每个 RTT 加 1 MSS。
- 超时：ssthresh = cwnd/2，cwnd 回到 1。
- 三个重复 ACK：快速重传 + 快速恢复，ssthresh = cwnd/2，cwnd = ssthresh（Reno）。

## HTTP 缓存
- 强缓存：Cache-Control: max-age，命中时不发请求。
- 协商缓存：ETag / If-None-Match，Last-Modified / If-Modified-Since，未变化返回 304。
- no-cache：可以存，但每次使用前必须向服务器确认；no-store：不存。

考试题型：选择 30%，简答 40%，计算（拥塞窗口变化）30%。
