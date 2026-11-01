// The agent supplies the learner's UI language, which may differ from the subject.
// Legacy cards can use host locale; content detection is only the final fallback.
export function normalizeLocale(value) {
  if (typeof value !== 'string') return undefined;
  if (/^zh(?:-|$)/i.test(value)) return 'zh-CN';
  if (/^en(?:-|$)/i.test(value)) return 'en';
  return undefined;
}
export function resolveLocale(card = {}, hostLocale) {
  const explicit = normalizeLocale(card.locale);
  if (explicit) return explicit;
  const host = normalizeLocale(hostLocale);
  if (host) return host;
  const context = [card.title, card.question, card.explanation, card.lesson].filter(Boolean).join(' ');
  return /[\u3400-\u9fff]/u.test(context) ? 'zh-CN' : 'en';
}

const zh = {
  pageTitle: 'closebook 学习卡片', card: '学习卡片', lesson: '学一点',
  kinds: { mcq: '选择题', free_text: '简答', numeric: '数值题', cloze_passage: '填空', order_steps: '排序', flashcard: '回忆卡' },
  continue: '继续练习', explainAgain: '换个例子再讲', submit: '提交答案', submitFlip: '提交并翻面', submitted: '已提交',
  dontKnow: '这题我还不会', confidence: '你有多大把握？', confidenceChoices: ['1 · 猜的', '2 · 比较确定', '3 · 很确定'],
  confidenceRequired: '请同时选择把握程度 1–3（1 = 猜的，2 = 比较确定，3 = 很确定）。',
  chooseConfidence: '请选择把握程度 1–3。', chooseNext: '请选择下一步。', chooseAnswer: '请先选择一个答案。',
  fill: label => `请填写${label}。`, eachBlank: '请填写每一空。', selectOrder: count => `请按顺序放入 ${count} 项。`,
  orderPrompt: count => `按顺序选出 ${count} 项：`, unitRequired: '请同时填写单位。',
  answerInCard: '请在卡片中作答并提交；如果卡片未显示，可以直接在对话中回答。',
  lessonFooter: '看完后可以继续练习，或请我换个例子再讲。阅读完成不代表已经掌握。',
  quizFooter: '如果看到了卡片，请点选并提交；如果只看到文字，请如实说明没有显示卡片。',
  order: '你的排列', pool: '待选项目',
  orderCount: (selected, count) => `已排列 ${selected} / ${count} 项 · 点选下方项目加入，顺序可以调整`,
  up: '上移', down: '下移', remove: '移回', moveItem: (label, number) => `${label}第 ${number} 项`,
  recallPrompt: '先凭记忆写下答案，再提交翻面', writtenPrompt: '用自己的话回答',
  answerLabel: '你的回答', valueLabel: '数值或表达式', unitLabel: '单位', workingLabel: '计算过程',
  requiredUnit: '单位（必填）', optionalUnit: '单位（选填）', optionalWorking: '计算过程（选填）', expression: '可填分数或表达式',
  nextCheck: '下一步，用一道小练习检验理解。', laterReference: '这张卡片的参考答案会由助手在你提交后给出。',
  reference: '参考答案', referenceNote: '这是对照参考，是否答对由助手根据你的原始作答判断。',
  preparing: '正在准备内容…', connecting: '正在连接对话…', sending: '正在提交…',
  sent: '已提交，回到对话查看反馈。', copyLabel: '可复制的回应文本',
  unconfirmed: '未收到提交确认。先检查对话里是否已有回应；若没有，可以复制下方文字发到对话。',
  invalidContent: '内容没有加载成功，请让助手重新发送。', incomplete: '题目数据不完整，请让助手重新发送。',
  unsupportedCard: '不支持这种卡片。', unsupportedType: '当前卡片版本不支持这个题型。',
  connectionError: '卡片连接出现问题。可以把答案发到对话，或让助手重新发送卡片。',
  connectionFailed: '当前客户端未建立卡片连接，可以直接在对话中继续学习。',
  notAccepted: '当前客户端没有接受这条作答消息。',
  responsePrefix: card => `我在 closebook 卡片中提交了回应。\n回应编号：${card.kind}:${card.id}\n标题：${card.title}`,
  continueMessage: '我已读完这段讲解，请出一道引导练习；这不表示我已经掌握。',
  explainMessage: '这段我还不清楚，请换个具体例子再解释。', continueLanguage: '请用中文继续。',
  unknownAnswer: '我的作答：这题我还不会。', choiceAnswer: option => `我的选择：${option.id}（${option.text}）`,
  textAnswer: value => `我的作答：\n${value}`, numberAnswer: value => `我的数值/表达式：${value}`,
  unitAnswer: value => `我的单位：${value}`, workingAnswer: value => `我的计算过程：\n${value}`,
  passageAnswer: (passage, answers) => `原文：${passage}\n我的填空：\n${answers}`,
  blankAnswer: (blank, value) => `${blank.label} [${blank.id}]：${value}`,
  orderAnswer: (ids, lines) => `我的顺序：${ids.join(' → ')}\n${lines}`,
  questionInfo: card => `题目编号：${card.id}\n题型：${card.type}\n题目：${card.question}`,
  confidenceAnswer: value => `把握程度：${value}`,
  feedback: '请按题意核对原始作答，接受合理的等价写法，并用中文反馈。',
};
const en = {
  pageTitle: 'closebook learning cards', card: 'Learning card', lesson: 'Learn a little',
  kinds: { mcq: 'Multiple choice', free_text: 'Written answer', numeric: 'Numeric answer', cloze_passage: 'Fill in the blanks', order_steps: 'Ordering', flashcard: 'Recall card' },
  continue: 'Continue to practice', explainAgain: 'Explain with another example', submit: 'Submit answer', submitFlip: 'Submit and reveal', submitted: 'Submitted',
  dontKnow: "I don't know yet", confidence: 'How confident are you?', confidenceChoices: ['1 · Guessing', '2 · Fairly sure', '3 · Very sure'],
  confidenceRequired: 'Also select confidence 1–3 (1 = guessing, 2 = fairly sure, 3 = very sure).',
  chooseConfidence: 'Choose confidence 1–3.', chooseNext: 'Choose what to do next.', chooseAnswer: 'Choose an answer first.',
  fill: label => `Please fill in ${label}.`, eachBlank: 'Please fill in every blank.', selectOrder: count => `Arrange ${count} items in order.`,
  orderPrompt: count => `Select ${count} items in order:`, unitRequired: 'Please include the unit.',
  answerInCard: 'Answer and submit in the card. If it is not visible, you can answer directly in chat.',
  lessonFooter: 'Continue to practice or ask for another example. Finishing the explanation does not demonstrate mastery.',
  quizFooter: 'If the card is visible, select and submit your answer. If you only see text, say that the card did not appear.',
  order: 'Your order', pool: 'Available items',
  orderCount: (selected, count) => `${selected} / ${count} items arranged · Select items below, then adjust their order`,
  up: 'Move up', down: 'Move down', remove: 'Remove', moveItem: (label, number) => `${label}: item ${number}`,
  recallPrompt: 'Write your answer from memory, then submit to reveal the reference', writtenPrompt: 'Answer in your own words',
  answerLabel: 'your answer', valueLabel: 'Value or expression', unitLabel: 'Unit', workingLabel: 'Working',
  requiredUnit: 'Unit (required)', optionalUnit: 'Unit (optional)', optionalWorking: 'Working (optional)', expression: 'Fractions or expressions are welcome',
  nextCheck: 'Next, try a short exercise to check your understanding.', laterReference: 'The assistant will give the reference answer after you submit.',
  reference: 'Reference answer', referenceNote: 'Use this for comparison. The assistant checks your original answer.',
  preparing: 'Preparing content…', connecting: 'Connecting to chat…', sending: 'Submitting…',
  sent: 'Submitted. Return to chat for feedback.', copyLabel: 'Response text to copy',
  unconfirmed: 'Submission was not confirmed. Check whether your response reached the chat. If it did not, copy the text below into chat.',
  invalidContent: 'The content did not load. Ask the assistant to send it again.', incomplete: 'The question data is incomplete. Ask the assistant to send it again.',
  unsupportedCard: 'This card is not supported.', unsupportedType: 'This card version does not support this question type.',
  connectionError: 'There is a card connection problem. Answer in chat or ask the assistant to resend the card.',
  connectionFailed: 'This client could not connect the card. You can continue learning in chat.',
  notAccepted: 'This client did not accept the answer message.',
  responsePrefix: card => `I submitted a response in a closebook card.\nResponse ID: ${card.kind}:${card.id}\nTitle: ${card.title}`,
  continueMessage: 'I have read this explanation. Please give me a guided exercise; this does not mean I have mastered it.',
  explainMessage: 'I am still unsure. Please explain with a different concrete example.', continueLanguage: 'Please continue in English.',
  unknownAnswer: "My answer: I don't know yet.", choiceAnswer: option => `My choice: ${option.id} (${option.text})`,
  textAnswer: value => `My answer:\n${value}`, numberAnswer: value => `My value/expression: ${value}`,
  unitAnswer: value => `My unit: ${value}`, workingAnswer: value => `My working:\n${value}`,
  passageAnswer: (passage, answers) => `Passage: ${passage}\nMy answers:\n${answers}`,
  blankAnswer: (blank, value) => `${blank.label} [${blank.id}]: ${value}`,
  orderAnswer: (ids, lines) => `My order: ${ids.join(' → ')}\n${lines}`,
  questionInfo: card => `Question ID: ${card.id}\nType: ${card.type}\nQuestion: ${card.question}`,
  confidenceAnswer: value => `Confidence: ${value}`,
  feedback: 'Check my original answer against the question, accept valid equivalent answers, and give feedback in English.',
};
export function messages(locale) { return normalizeLocale(locale) === 'zh-CN' ? zh : en; }
