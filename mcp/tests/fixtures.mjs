export const sampleLesson = {
  id: 'free-fall-chunk-1', title: '自由落体：速度怎样变化',
  explanation: '忽略空气阻力，从静止释放的小球会越来越快。靠近地面时，速度每秒约增加 9.8 米/秒。',
  example: { title: '先看一个例子', text: '取向下为正方向：释放时速度为 0；经过 1 秒约为 9.8 米/秒。\n这描述的是速度如何变化，还不是下落距离。' },
  takeaway: '重力加速度描述速度随时间的变化。',
};
export const sampleExercises = [
  { id: 'mcq-1', type: 'mcq', title: '细胞结构', question: '哪种结构主要控制物质进出细胞？', options: [{ id: 'A', text: '细胞膜' }, { id: 'B', text: '细胞核' }] },
  { id: 'written-1', type: 'free_text', title: '用自己的话解释', question: '为什么分数 1/2 与 2/4 相等？用自己的话说明。' },
  { id: 'number-1', type: 'numeric', title: '计算斜率', question: '经过 (2, 3) 和 (4, 2) 的直线，斜率是多少？', requireUnit: false },
  { id: 'cloze-1', type: 'cloze_passage', title: '现在完成时', question: '根据上下文补全两个空，允许缩写。', passage: 'I {{known}} her for years. She {{seen}} him since Monday.（第二句填否定形式）', blanks: [{ id: 'known', label: '第 1 空：know' }, { id: 'seen', label: '第 2 空：see，否定' }] },
  { id: 'order-1', type: 'order_steps', title: 'Git 提交流程', question: '选择三项组成“修改文件并提交”的顺序，排除无关项。', items: [{ id: 'commit', text: '提交暂存内容' }, { id: 'delete', text: '删除整个仓库' }, { id: 'edit', text: '编辑目标文件' }, { id: 'stage', text: '暂存目标文件' }], pickCount: 3 },
  { id: 'recall-1', type: 'flashcard', title: '生物词汇', question: 'mitochondrion 的中文名称是什么？', reference: '线粒体。它是进行细胞呼吸的重要场所。' },
];
