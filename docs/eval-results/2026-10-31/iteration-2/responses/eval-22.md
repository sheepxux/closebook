好，今天就到这。先看复习安排：

**复习清单**
- **2026-11-01（明天）**，按这个顺序：
  1. **kp3 超时与快速恢复**：排第一。这次是信心 3 却答错，属于最值得抓住的那种错：你把超时时的处理套到了"收到三个重复 ACK"上。
  2. **kp2 拥塞避免**：答对了一部分，增长规则没想起来。
  3. **kp1 慢启动**：答对了。明天第一次就答对的话，下次复习就排到 3 天后。

今天学的点明天都要复习，这是故意的：第一次复习最有用。

综合环节的自由回忆是对整个主题答的，我没把它拆到单个知识点上计分；反正三个点明天都要复习，不影响安排。

换一个新对话我就不记得今天的内容了，进度全在下面这段里。把它整段复制存好（备忘录之类的地方都行），下次贴回来就能接着复习：

```json
{"schema_version":"1.0","profile":"core","topic":"TCP 拥塞控制","language":"zh-CN","created":"2026-10-31","updated":"2026-10-31","settings":{"leitner_intervals_days":[1,3,7,14,30],"review_batch_size":8,"interleaving":"auto"},"knowledge_points":[{"id":"kp1","title":"慢启动","importance":"core","knowledge_type":"procedural","status":"active","mastery":"solid","leitner_box":1,"next_review":"2026-11-01","last_reviewed":"2026-10-31","attempts":[{"id":"kp1-1","at":"2026-10-31","phase":"retest","result":"correct","hint_level":0,"confidence":2}]},{"id":"kp2","title":"拥塞避免","importance":"important","knowledge_type":"procedural","status":"active","mastery":"fuzzy","leitner_box":1,"next_review":"2026-11-01","last_reviewed":"2026-10-31","attempts":[{"id":"kp2-1","at":"2026-10-31","phase":"retest","result":"partial","hint_level":0,"confidence":2,"error_type":"memory_lapse"}],"errors":[{"at":"2026-10-31","error_type":"memory_lapse","high_confidence":false,"remedy":"下次复习先闭卷重新回忆增长规则；可以编一句口诀记住“每个 RTT 加 1 MSS”","resolved":false}]},{"id":"kp3","title":"超时与快速恢复","importance":"core","knowledge_type":"conceptual","status":"active","mastery":"weak","leitner_box":1,"next_review":"2026-11-01","last_reviewed":"2026-10-31","priority_flag":true,"attempts":[{"id":"kp3-1","at":"2026-10-31","phase":"diagnostic","result":"dont_know","hint_level":0},{"id":"kp3-2","at":"2026-10-31","phase":"retest","result":"incorrect","hint_level":0,"confidence":3,"error_type":"misconception"}],"errors":[{"at":"2026-10-31","error_type":"misconception","high_confidence":true,"remedy":"用“超时 vs 三个重复 ACK”的对比例子打破错误模型；追问为什么两者处理不同；换个问法重测","resolved":false}]}],"weak_points":[{"kp_id":"kp3","note":"以为收到三个重复 ACK 后 cwnd 降到 1（信心 3 答错），把超时和快速恢复的处理混为一谈"},{"kp_id":"kp2","note":"没想起拥塞避免阶段每个 RTT 只把 cwnd 加 1 MSS"}]}
```

下次开新对话时把它贴给我，我会先出题让你凭记忆回答，答完再讲解。
