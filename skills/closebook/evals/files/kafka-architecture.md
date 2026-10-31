# Kafka architecture (study notes)

- A **topic** is split into **partitions**. Each partition is an ordered, append-only log; ordering is guaranteed only within a partition.
- Producers choose the partition, usually by hashing the message key, so messages with the same key land in the same partition and stay in order.
- Each partition has one **leader** broker and several **followers** (replicas). Producers and consumers talk to the leader; followers copy its log. If the leader fails, an in-sync follower becomes leader.
- Consumers join a **consumer group**. Each partition is read by exactly one consumer in the group, so a group with more consumers than partitions leaves some consumers idle.
- Each consumer group tracks its own **offset** per partition (its position in the log). Committing the offset after processing gives at-least-once delivery; committing before processing risks losing messages on a crash.
- When a consumer joins, leaves or crashes, the group **rebalances**: partitions are reassigned among the remaining consumers, which resume from the last committed offsets.
