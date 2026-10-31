"""End-to-end test of the HTML lesson page in headless Chromium.

Skipped unless Playwright and its Chromium are installed:
    pip install playwright && python -m playwright install chromium-headless-shell
"""
from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "closebook")
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import build_lesson  # noqa: E402
import progress_tool  # noqa: E402

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

ZH_LESSON = os.path.join(SKILL, "schemas", "examples", "lesson.http-cache.json")
SHOWCASE = os.path.join(ROOT, "tests", "fixtures", "showcase.lesson.json")
PROGRESS = os.path.join(SKILL, "schemas", "examples", "progress.full.json")
SUBJECTS = os.path.join(SKILL, "schemas", "examples", "lesson.subjects.json")


def _build(lesson, directory, name):
    with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
        html = build_lesson.embed(lesson, fh.read())
    path = os.path.join(directory, name)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return "file://" + path


@unittest.skipIf(sync_playwright is None, "playwright not installed")
class LessonPageE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.pw = sync_playwright().start()
        try:
            cls.browser = cls.pw.chromium.launch()
        except Exception as exc:  # pragma: no cover
            cls.pw.stop()
            raise unittest.SkipTest("chromium unavailable: %s" % exc)
        cls.zh_url = _build(progress_tool.load_json(ZH_LESSON), cls.tmp.name, "zh.html")
        cls.showcase = progress_tool.load_json(SHOWCASE)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.tmp.cleanup()

    def open(self, url, **context_args):
        context = self.browser.new_context(**context_args)
        self.addCleanup(context.close)
        page = context.new_page()
        page.set_default_timeout(5000)
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("dialog", lambda dialog: dialog.accept())
        page.goto(url)
        self.addCleanup(lambda: self.assertEqual(errors, [], "page errors"))
        return page

    @staticmethod
    def btn(page, name):
        return page.get_by_role("button", name=name, exact=True)

    @staticmethod
    def tab(page, name):
        return page.get_by_role("tab", name=name, exact=True)

    @staticmethod
    def progress(page):
        return page.locator("#progress p").inner_text()

    def export_json(self, page):
        page.get_by_role("tab").last.click()
        page.locator("[role=tabpanel] section.card").first.locator("button").first.click()
        return json.loads(page.locator("textarea.export-area").first.input_value())

    def complete_zh_lesson(self, page):
        self.assertEqual(page.get_by_role("tab").count(), 5)
        self.assertEqual(self.progress(page), "已作答 0 / 7 题")

        # kp1 diagram_fill: one blank auto-matches, the other is wrong -> partial
        blanks = page.locator(".flow input[type=text]")
        blanks.nth(0).fill("带 ETag 发请求")
        blanks.nth(1).fill("200 从缓存读")
        self.assertNotIn("返回 304", page.locator(".flow").inner_text(), "blank answer leaked before checking")
        self.btn(page, "提交").click()
        marks = page.get_by_label("算对")
        self.assertTrue(marks.nth(0).is_checked())
        self.assertFalse(marks.nth(1).is_checked())
        self.btn(page, "确认").click()
        self.assertIn("部分正确", page.locator(".result").inner_text())
        self.btn(page, "概念误解").click()
        self.btn(page, "下一个知识点").click()

        # kp2 mcq: the submit button needs both an answer and a confidence
        page.locator("label.option", has_text="浏览器不能存储").click()
        self.assertTrue(self.btn(page, "提交").is_disabled())
        page.locator("label.chip", has_text="3 · 很确定").click()
        self.btn(page, "提交").click()
        card = page.locator("section.card").nth(1)
        self.assertIn("高信心答错", card.inner_text())
        self.assertIn("s-maxage", card.inner_text(), "every option should show its explanation")
        self.btn(page, "概念误解").click()
        page.locator("label.option", has_text="immutable").click()
        page.locator("label.chip", has_text="2 · 比较确定").click()
        self.btn(page, "提交").click()
        self.assertIn("正确", page.locator("section.card").nth(2).locator(".result").inner_text())
        self.btn(page, "下一个知识点").click()

        # kp3 plain_qa: case-sensitive miss, then "I was actually right"; then "don't know"
        page.get_by_placeholder("你的答案").fill("--HEAD")
        page.locator("label.chip", has_text="2 · 比较确定").click()
        self.btn(page, "提交").click()
        self.assertIn("不对", page.locator(".result").inner_text())
        page.get_by_role("button", name="其实我答对了").click()
        self.assertIn("正确", page.locator(".result").first.inner_text())
        self.btn(page, "不知道").click()
        self.assertIn("已记为“不知道”", page.locator("section.card").nth(2).inner_text())
        self.assertIn("304", page.locator("section.card").nth(2).inner_text(), "reference answer after dont_know")
        self.btn(page, "下一个知识点").click()

        # kp4 compare_table_fill: all three blanks right
        cells = page.locator("table.fill input[type=text]")
        self.assertEqual(cells.count(), 3)
        for i, value in enumerate(["no-cache", "max-age=31536000, immutable", "no-store"]):
            cells.nth(i).fill(value)
        self.btn(page, "提交").click()
        self.btn(page, "确认").click()
        self.assertIn("正确", page.locator(".result").inner_text())
        self.btn(page, "下一个知识点").click()

        # kp6 free_text behind the teaching gate
        self.assertEqual(page.get_by_placeholder("你的答案").count(), 0, "questions must stay hidden while teaching")
        self.assertIn("ETag", page.locator(".teach").inner_text())
        self.btn(page, "合上讲解，凭记忆作答").click()
        self.assertEqual(page.locator(".teach").count(), 0, "teaching must close before answering")
        page.get_by_placeholder("你的答案").fill("重新部署后时间变了但内容没变。")
        self.btn(page, "提交").click()
        self.assertIn("这是自评，不是自动批改", page.locator("body").inner_text())
        page.locator(".checklist label", has_text="修改时间变了").locator("input").check()
        self.btn(page, "确认自评").click()
        self.assertIn("部分正确", page.locator(".result").inner_text())
        self.assertIn("全部知识点已完成", page.locator("body").inner_text())
        self.assertEqual(self.progress(page), "已作答 7 / 7 题")

        # free recall
        self.tab(page, "自由回忆").click()
        page.locator("[role=tabpanel] textarea").fill("没过期直接用，过期了带 ETag 问，304。")
        self.btn(page, "与要点对照").click()
        page.locator(".checklist label", has_text="没过期直接用本地副本").locator("input").check()
        page.locator(".checklist label", has_text="过期后带 ETag 询问").locator("input").check()
        self.btn(page, "确认自评").click()

        # plain talk: analogy limits shown, then hidden before the recall
        self.tab(page, "小白模式").click()
        text = page.locator("[role=tabpanel]").inner_text()
        self.assertIn("这个类比哪里不成立", text)
        self.assertIn("这里不用类比", text)
        self.btn(page, "我准备好了，隐藏上面的讲解").click()
        self.assertNotIn("冰箱里的牛奶", page.locator("[role=tabpanel]").inner_text())
        page.locator("[role=tabpanel] textarea").fill("入口文件地址不变，强缓存会让用户看不到新版本。")
        self.btn(page, "对照讲解").click()
        self.btn(page, "部分对").click()

    def test_full_flow_export_validates_and_imports(self):
        page = self.open(self.zh_url)
        self.complete_zh_lesson(page)

        self.tab(page, "错题").click()
        mistakes = page.locator("[role=tabpanel]").inner_text()
        self.assertIn("概念误解", mistakes)
        self.assertEqual(page.locator(".badge.hot").count(), 1)
        groups = page.locator("section.group h3").all_inner_texts()
        self.assertEqual(groups[0].split(" · ")[0], "概念误解")
        page.locator("section.group").last.locator("select").first.select_option("memory_lapse")
        self.assertIn("记忆遗漏", page.locator("section.group h3").all_inner_texts()[1])

        export = self.export_json(page)
        self.assertEqual(export["format"], "closebook-session-export")
        self.assertEqual(sorted(export["plain_talk_viewed_kp_ids"]), ["kp1", "kp2", "kp4"])
        phases = sorted({a.get("phase", "-") for a in export["attempts"]})
        self.assertEqual(phases, ["plain_talk_recall", "retest", "synthesis"])
        self.assertEqual(progress_tool.validate_export(export), [])
        hot = [a for a in export["attempts"] if a.get("confidence") == 3 and a["result"] == "incorrect"]
        self.assertEqual(len(hot), 1)
        self.assertEqual(hot[0]["error_type"], "misconception")
        override = [a for a in export["attempts"] if a.get("question", "").startswith("只看响应头")][0]
        self.assertEqual((override["result"], override.get("self_assessed")), ("correct", True))

        merged = progress_tool.import_session(copy.deepcopy(progress_tool.load_json(PROGRESS)), export)
        problems = [i for i in progress_tool.validate_progress(merged) if i.severity == "error"]
        self.assertEqual(problems, [])
        again = progress_tool.import_session(copy.deepcopy(merged), export)
        self.assertEqual(again, merged, "re-importing the same export must be a no-op")

        page.locator("textarea.export-area").nth(1).evaluate("e => e.value = ''")
        self.btn(page, "生成").nth(1).click()
        answers = page.locator("textarea.export-area").nth(1).input_value()
        self.assertIn("# closebook · 我的作答", answers)
        self.assertIn("- [x] 文件内容没变但修改时间变了", answers)
        self.assertIn("- [ ] 一秒内多次修改", answers)

        # same export again -> nothing new; another lesson -> refused
        box = page.locator("textarea.import-area")
        box.fill(json.dumps(export, ensure_ascii=False))
        self.btn(page, "合并").click()
        self.assertIn("没有新的作答需要合并", page.locator("body").inner_text())
        other = dict(export, lesson_id="something-else")
        box.fill(json.dumps(other))
        self.btn(page, "合并").click()
        self.assertIn("另一节课", page.locator("body").inner_text())
        box.fill("{not json")
        self.btn(page, "合并").click()
        self.assertIn("这不是 closebook 导出的进度", page.locator("body").inner_text())

        # a fresh browser (no localStorage) restores everything from the export
        fresh = self.open(self.zh_url)
        self.assertEqual(self.progress(fresh), "已作答 0 / 7 题")
        self.tab(fresh, "保存与导入").click()
        fresh.locator("textarea.import-area").fill(json.dumps(export, ensure_ascii=False))
        self.btn(fresh, "合并").click()
        self.assertIn("合并了 %d 条新作答" % len(export["attempts"]), fresh.locator("body").inner_text())
        self.assertEqual(self.progress(fresh), "已作答 7 / 7 题")
        self.tab(fresh, "学习").click()
        self.assertIn("之前已作答", fresh.locator("body").inner_text())

        # localStorage survives a reload in the same browser
        page.reload()
        self.assertEqual(self.progress(page), "已作答 7 / 7 题")

    def test_retry_records_a_second_attempt(self):
        page = self.open(self.zh_url)
        page.locator(".flow input[type=text]").nth(0).fill("x")
        self.btn(page, "提交").click()
        self.btn(page, "确认").click()
        self.assertIn("不对", page.locator(".result").inner_text())
        self.btn(page, "再试一次").click()
        blanks = page.locator(".flow input[type=text]")
        self.assertEqual(blanks.nth(0).input_value(), "")
        blanks.nth(0).fill("if-none-match")
        blanks.nth(1).fill("304")
        self.btn(page, "提交").click()
        self.btn(page, "确认").click()
        self.assertIn("正确", page.locator(".result").inner_text())
        attempts = self.export_json(page)["attempts"]
        self.assertEqual([a["result"] for a in attempts], ["incorrect", "correct"])
        self.assertEqual(len({a["id"] for a in attempts}), 2)

    def test_coach_grading_round_trip(self):
        page = self.open(self.zh_url)
        self.complete_zh_lesson(page)
        export = self.export_json(page)
        written = [a for a in export["attempts"] if a.get("interaction") == "free_text" and a["phase"] == "retest"][0]
        recall = [a for a in export["attempts"] if a["phase"] == "plain_talk_recall"][0]
        curl = [a for a in export["attempts"] if a.get("question", "").startswith("只看响应头")][0]

        self.btn(page, "生成").nth(1).click()
        answers = page.locator("textarea.export-area").nth(1).input_value()
        self.assertIn("closebook-grading", answers, "the export tells the coach how to reply")
        self.assertIn("带 ETag 发请求 / 200 从缓存读", answers, "filled blanks are exported for grading")
        for attempt in (written, recall):
            self.assertIn("**ID:** `%s`" % attempt["id"], answers)

        grading = {
            "format": "closebook-grading", "schema_version": "1.0", "lesson_id": export["lesson_id"],
            "graded_at": "2026-10-31T22:00:00+08:00",
            "grades": [
                {"attempt_id": written["id"], "result": "correct", "feedback": "抓住了“内容没变但时间变了”，这就是关键。"},
                {"attempt_id": recall["id"], "result": "incorrect", "error_type": "misconception",
                 "feedback": "说反了：入口文件要每次确认，长缓存留给带哈希的文件。"},
                {"attempt_id": curl["id"], "result": "incorrect", "feedback": "curl 不认 --HEAD，要用 --head 或 -I。"},
            ],
        }
        self.assertEqual(progress_tool.validate_grading(grading), [])
        box = page.locator("textarea.import-area")
        box.fill("```json\n%s\n```" % json.dumps(grading, ensure_ascii=False))
        self.btn(page, "合并").click()
        self.assertIn("已应用教练的 3 条批改", page.locator("body").inner_text())
        self.btn(page, "合并").click()
        self.assertIn("这些批改之前已经应用过了", page.locator("body").inner_text())
        box.fill(json.dumps(dict(grading, grades=[{"attempt_id": "ghost", "result": "correct"}])))
        self.btn(page, "合并").click()
        self.assertIn("有 1 条批改对不上本页的作答", page.locator("body").inner_text())
        box.fill(json.dumps(dict(grading, lesson_id="something-else")))
        self.btn(page, "合并").click()
        self.assertIn("另一节课", page.locator("body").inner_text())

        self.tab(page, "学习").click()
        page.locator(".stepper button").nth(4).click()
        result = page.locator(".result").first.inner_text()
        self.assertIn("正确", result)
        self.assertIn("教练批改", result)
        self.assertIn("内容没变但时间变了", result)
        self.assertNotIn("自评", result)
        page.locator(".stepper button").nth(2).click()
        self.assertIn("curl 不认 --HEAD", page.locator("[role=tabpanel]").inner_text())
        self.assertEqual(page.get_by_role("button", name="其实我答对了").count(), 0,
                         "the learner can't overrule the coach in the page; disputes go to the chat")

        self.tab(page, "小白模式").click()
        self.assertIn("长缓存留给带哈希的文件", page.locator(".result").inner_text())

        self.tab(page, "错题").click()
        mistakes = page.locator("[role=tabpanel]").inner_text()
        self.assertIn("长缓存留给带哈希的文件", mistakes)
        self.assertIn("教练批改", mistakes)

        graded = self.export_json(page)
        self.assertEqual(progress_tool.validate_export(graded), [])
        by_id = {a["id"]: a for a in graded["attempts"]}
        self.assertEqual((by_id[written["id"]]["result"], by_id[written["id"]]["coach_graded"]), ("correct", True))
        self.assertNotIn("self_assessed", by_id[written["id"]])
        self.assertEqual(by_id[recall["id"]]["error_type"], "misconception")
        merged = progress_tool.import_session(copy.deepcopy(progress_tool.load_json(PROGRESS)), graded)
        self.assertEqual([i for i in progress_tool.validate_progress(merged) if i.severity == "error"], [])

        page.reload()
        self.tab(page, "错题").click()
        self.assertIn("长缓存留给带哈希的文件", page.locator("[role=tabpanel]").inner_text(), "grades survive a reload")

    def test_keyboard_theme_and_layout(self):
        page = self.open(self.zh_url, color_scheme="dark", viewport={"width": 375, "height": 800})
        bg = lambda: page.evaluate("getComputedStyle(document.body).backgroundColor")
        light_bg = bg()
        self.assertEqual(page.locator("#theme").input_value(), "light", "light by default, even when the OS is dark")
        page.locator("#theme").select_option("auto")
        self.assertNotEqual(bg(), light_bg, "auto follows the dark OS setting")
        page.locator("#theme").select_option("dark")
        dark_bg = bg()
        self.assertNotEqual(dark_bg, light_bg)
        page.locator("#theme").select_option("light")
        self.assertEqual(bg(), light_bg)
        self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), 376, "horizontal overflow on mobile")

        page.get_by_role("tab", name="学习").focus()
        page.keyboard.press("ArrowRight")
        self.assertEqual(page.evaluate("document.activeElement.textContent"), "自由回忆")
        self.assertEqual(page.get_by_role("tab", selected=True).inner_text(), "自由回忆")
        page.keyboard.press("ArrowLeft")
        page.keyboard.press("ArrowLeft")
        self.assertEqual(page.get_by_role("tab", selected=True).inner_text(), "保存与导入")

        # MCQ answerable with the keyboard only
        self.tab(page, "学习").click()
        self.btn(page, "2. Cache-Control 指令与 304 状态码 · 未开始").click()
        page.locator("label.option input").first.focus()
        page.keyboard.press("ArrowDown")
        page.locator("label.chip input").first.focus()
        page.keyboard.press("Space")
        page.locator("button[type=submit]").focus()
        page.keyboard.press("Enter")
        self.assertIn("正确", page.locator(".result").first.inner_text())
        self.assertEqual(page.evaluate("document.activeElement.className"), "result correct",
                         "focus should move to the result after submitting")

    def test_showcase_components_and_fallbacks(self):
        lesson = copy.deepcopy(self.showcase)
        lesson["knowledge_points"].append({
            "id": "kp5", "title": "Unknown widget", "importance": "minor", "knowledge_type": "factual",
            "interaction_type": "drag_sort", "interaction_reason": "future type",
            "items": [{"id": "u1", "question": "Which status means Not Modified?", "answer": "304", "accept": ["304"]}],
        })
        page = self.open(_build(lesson, self.tmp.name, "showcase.html"))
        self.assertEqual(page.get_by_role("tab").all_inner_texts(), ["Learn", "Mistakes", "Save & load"])
        self.assertEqual(page.locator(".teach").count(), 0)

        cells = page.locator("table.fill input[type=text]")
        cells.nth(0).fill("1996")
        cells.nth(1).fill("2016")
        self.btn(page, "Check").click()
        self.btn(page, "Confirm").click()
        self.assertIn("Partly right", page.locator(".result").inner_text())
        self.btn(page, "Next point").click()

        self.assertIn("no interactive simulation", page.locator("body").inner_text())
        page.get_by_placeholder("Your answer").fill("One")
        page.locator("label.chip", has_text="2 · fairly sure").click()
        self.btn(page, "Check").click()
        self.assertIn("Correct", page.locator(".result").inner_text())
        self.btn(page, "Next point").click()

        self.assertEqual(page.locator("label.chip", has_text="fairly sure").count(), 0, "no confidence on contested points")
        page.get_by_placeholder("Your answer").fill("No: a cache key mistake leaks one user's page to another.")
        self.btn(page, "Check").click()
        for box in page.locator(".checklist input").all():
            box.check()
        self.btn(page, "Confirm self-check").click()
        self.assertIn("Your reasoning holds together", page.locator(".result").inner_text())
        self.btn(page, "Next point").click()

        page.get_by_placeholder("Your answer").fill("304")
        self.assertTrue(self.btn(page, "Flip the card").is_disabled())
        page.locator("label.chip", has_text="3 · certain").click()
        self.assertEqual(page.locator(".flashcard.back").count(), 0, "answer must stay hidden before flipping")
        self.btn(page, "Flip the card").click()
        self.assertEqual(page.locator(".flashcard.back").inner_text(), "304")
        self.btn(page, "Got it").click()
        self.btn(page, "Next point").click()

        self.assertIn("isn't supported here", page.locator("body").inner_text())
        page.get_by_placeholder("Your answer").fill("304")
        page.locator("label.chip", has_text="1 · guessing").click()
        self.btn(page, "Check").click()
        self.assertIn("Correct", page.locator(".result").inner_text())

        export = self.export_json(page)
        self.assertEqual({a["phase"] for a in export["attempts"]}, {"review"})
        coherent = [a for a in export["attempts"] if a["kp_id"] == "kp3"][0]
        self.assertEqual(coherent["result"], "coherent")
        self.assertNotIn("confidence", coherent)
        self.assertEqual(progress_tool.validate_export(export), [])

    @staticmethod
    def focused(page, prop="textContent"):
        return page.evaluate("p => document.activeElement && (document.activeElement[p] || document.activeElement.getAttribute(p))", prop)

    def test_subject_widgets(self):
        page = self.open(_build(progress_tool.load_json(SUBJECTS), self.tmp.name, "subjects.html"))
        self.assertEqual(self.progress(page), "已作答 0 / 10 题")
        conf = lambda c: page.locator("label.chip", has_text=c).click()  # noqa: E731
        nxt = lambda: self.btn(page, "下一个知识点").click()  # noqa: E731

        # numeric: expressions are evaluated, units stripped, tolerance applied
        box = page.get_by_placeholder("数字或算式，如 0.75、3/4、2*pi")
        box.fill("abc")
        self.assertEqual(page.locator(".reads").inner_text(), "还无法识别为数字")
        box.fill("50/2 m")
        self.assertEqual(page.locator(".reads").inner_text(), "识别为 25 m")
        self.assertTrue(self.btn(page, "提交").is_disabled(), "confidence still missing")
        conf("2 · 比较确定")
        self.btn(page, "提交").click()
        self.assertIn("正确", page.locator(".result").inner_text())
        page.get_by_placeholder("数字或算式，如 0.75、3/4、2*pi").fill("1,100")
        conf("3 · 很确定")
        self.btn(page, "提交").click()
        card = page.locator("section.card").nth(2)
        self.assertIn("高信心答错", card.inner_text())
        self.assertIn("1102.5 元", card.inner_text())
        self.assertIn("解题步骤", card.inner_text())
        nxt()

        # order_steps (Parsons): tap into place, fix with arrows, focus follows the moved line
        def place(text):
            items = page.locator(".pool-item")
            items.nth(items.evaluate_all("(els, t) => els.findIndex(e => e.textContent === t)", text)).click()
        lines = ["def sum_even(nums):", "    total = 0", "        if n % 2 == 0:", "    for n in nums:", "            total += n", "    return total"]
        for line in lines:
            place(line)
        self.assertTrue(page.locator(".pool-item").first.is_disabled(), "pool closes when every slot is full")
        self.assertEqual(page.locator(".pool-item").count(), 2, "the two distractors stay unused")
        page.get_by_role("button", name="前移：for n in nums:").click()
        self.assertEqual(self.focused(page, "aria-label"), "前移：for n in nums:")
        conf("2 · 比较确定")
        self.btn(page, "提交").click()
        self.assertIn("正确", page.locator(".result").inner_text())
        self.assertEqual(page.locator(".order-list li.ok").count(), 6)
        nxt()

        # order_steps (tiles): a distractor costs one position -> partial, correct order shown
        for word in ["She", "didn't", "went", "to", "school", "yesterday."]:
            place(word)
        conf("1 · 猜的")
        self.btn(page, "提交").click()
        self.assertIn("部分正确", page.locator(".result").inner_text())
        self.assertEqual(page.locator(".order-list li.bad .txt").inner_text(), "went")
        self.assertIn("不属于这里的：went", page.locator("body").inner_text())
        nxt()

        # cloze_passage: word bank fills the next blank and keeps focus; variants accepted
        page.get_by_role("button", name="二氧化碳", exact=True).click()
        self.assertEqual(self.focused(page), "二氧化碳")
        blanks = page.locator(".cloze input[type=text]")
        self.assertEqual(blanks.nth(0).input_value(), "二氧化碳")
        blanks.nth(1).fill("H₂O")
        blanks.nth(2).fill("葡萄糖")
        blanks.nth(3).fill("氮气")
        self.btn(page, "提交").click()
        self.assertEqual(page.get_by_label("算对").evaluate_all("els => els.map(e => e.checked)"), [True, True, True, False])
        self.btn(page, "确认").click()
        self.assertIn("部分正确", page.locator(".result").inner_text())
        nxt()

        # code_trace: predictions first, then the step player
        self.assertEqual(page.locator(".trace").count(), 0, "trace hidden before predicting")
        qs = page.locator(".trace-qs input[type=text]")
        qs.nth(0).fill("14")
        qs.nth(1).fill("4")
        self.btn(page, "提交").click()
        self.assertIn("第 1 / 8 步 · 第 1 行", page.locator(".trace").inner_text())
        for _ in range(6):
            self.btn(page, "下一步").click()
        self.assertEqual(self.focused(page), "下一步")
        self.assertEqual(page.locator(".code-lines .ln.cur").get_attribute("data-n"), "3")
        self.assertEqual(page.locator(".trace tr.changed th").inner_text(), "total")
        self.btn(page, "下一步").click()
        self.assertEqual(page.locator(".trace pre.out").inner_text(), "14")
        self.assertTrue(self.btn(page, "下一步").is_disabled())
        self.btn(page, "确认").click()
        self.assertIn("部分正确", page.locator(".result").inner_text())
        nxt()

        # terminal: scripted output, honest rejection, hint, reveal
        term = page.locator(".term-in")
        term.fill("git init")
        term.press("Enter")
        self.assertIn("Initialized empty Git repository", page.locator(".term").inner_text())
        self.assertEqual(self.focused(page, "className"), "term-in", "focus stays in the terminal")
        page.locator(".term-in").fill("git  add")
        page.locator(".term-in").press("Enter")
        self.assertIn("这一步要的不是这条命令", page.locator(".term").inner_text())
        self.btn(page, "给个提示").click()
        self.assertIn("跟一个点", page.locator("body").inner_text())
        page.locator(".term-in").fill("git   add  .")
        page.locator(".term-in").press("Enter")
        self.assertIn("第 3 / 3 步", page.locator("body").inner_text())
        self.btn(page, "看答案").click()
        self.assertIn('git commit -m "first commit"  （看了答案）', page.locator(".term").inner_text())
        self.assertIn("部分正确", page.locator(".result").inner_text())
        nxt()

        # graph (match): own curve hidden until the first check
        self.assertEqual(page.locator("svg.plot path.target").count(), 1)
        self.assertEqual(page.locator("svg.plot path.curve").count(), 0)
        sliders = page.locator("input[type=range]")
        sliders.nth(0).fill("0.5")
        sliders.nth(1).fill("2")
        sliders.nth(2).fill("-2")
        self.btn(page, "提交").click()
        self.assertIn("还没对上", page.locator("body").inner_text())
        self.assertEqual(page.locator("svg.plot path.curve").count(), 1)
        page.locator("input[type=range]").nth(2).fill("-3")
        self.btn(page, "提交").click()
        self.assertIn("部分正确", page.locator(".result").inner_text())
        self.assertIn("目标：a = 0.5, h = 2, k = -3", page.locator("body").inner_text())
        nxt()

        # graph (predict): sliders locked until the prediction is in
        self.assertTrue(page.locator("input[type=range]").first.is_disabled())
        page.locator("label.option", has_text="周期减半").click()
        conf("2 · 比较确定")
        self.btn(page, "提交").click()
        self.assertIn("正确", page.locator(".result").inner_text())
        before = page.locator("svg.plot path.curve").get_attribute("d")
        page.locator("input[type=range]").nth(1).fill("2")
        self.assertNotEqual(page.locator("svg.plot path.curve").get_attribute("d"), before, "curve redraws as the slider moves")
        nxt()

        # simulation (parameter lab): no graph before predicting; readouts follow the sliders
        self.assertEqual(page.locator("svg.plot").count(), 0, "the graph would give the prediction away")
        self.assertIn("2.01 s", page.locator(".readouts").inner_text())
        page.locator("label.option", has_text="4 倍").click()
        conf("3 · 很确定")
        self.btn(page, "提交").click()
        self.assertIn("高信心答错", page.locator(".result").inner_text())
        self.assertEqual(page.locator("svg.plot").count(), 1)
        page.locator("input[type=range]").first.fill("4")
        self.assertIn("4.01 s", page.locator(".readouts").inner_text())
        self.assertEqual(self.progress(page), "已作答 10 / 10 题")

        export = self.export_json(page)
        self.assertEqual(progress_tool.validate_export(export), [])
        by_kp = {a["kp_id"]: a for a in export["attempts"]}
        self.assertEqual({a["interaction"] for a in export["attempts"]},
                         {"numeric", "order_steps", "cloze_passage", "code_trace", "terminal", "graph", "simulation"})
        self.assertEqual(by_kp["kp-git"]["hint_level"], 3)
        self.assertEqual(by_kp["kp-sine"]["question_format"], "predict")
        self.assertNotIn("self_assessed", by_kp["kp-parsons"])

        page.get_by_role("button", name="生成").nth(1).click()
        answers = page.locator("textarea.export-area").nth(1).input_value()
        self.assertIn("1,100 (= 1100 元)", answers)
        self.assertIn("She didn't went to school yesterday.", answers)
        self.assertIn('~/demo $ git commit -m "first commit" （看了答案）', answers)
        self.assertIn("最后打印出什么？ → 14", answers)
        self.assertIn("二氧化碳 / H₂O / 葡萄糖 / 氮气", answers)
        self.assertIn("a = 0.5, h = 2, k = -3", answers)
        self.assertIn("B. 4 倍", answers)

    def test_trace_answer_spacing_preserves_string_contents(self):
        cases = [
            ("[4, 6]", "[ 4,6 ]", "container", True),
            ("['a, b', 2]", "[ 'a, b',2 ]", "container", True),
            ("['a, b', 2]", "['a,b',2]", "container", False),
            ("['a  b']", "['a b']", "container", False),
            ("hello, world", "hello,world", None, False),
            ("True", "true", None, False),
            ("[4, 6]", "(4, 6)", "container", False),
            ("(hello, world)", "(hello,world)", None, False),
            ("[a, b]", "[a,b]", None, False),
            ("[1, 2]", "[1,2]", "exact", False),
        ]
        for n, (answer, typed, comparison, expected) in enumerate(cases):
            with self.subTest(answer=answer, typed=typed):
                lesson = progress_tool.load_json(SUBJECTS)
                kp = next(k for k in lesson["knowledge_points"] if k["interaction_type"] == "code_trace")
                lesson["knowledge_points"] = [kp]
                kp["items"][0]["questions"] = [{"question": "输出是什么？", "answer": answer}]
                if comparison:
                    kp["items"][0]["questions"][0]["comparison"] = comparison
                page = self.open(_build(lesson, self.tmp.name, "trace-spacing-%d.html" % n))
                page.locator(".trace-qs input").fill(typed)
                self.btn(page, "提交").click()
                self.assertEqual(page.get_by_label("算对").is_checked(), expected)
                page.context.close()

    def test_terminal_equivalence_keeps_argument_binding(self):
        cases = [
            ("git log --graph --oneline --all --decorate", "git log --all --decorate --oneline --graph", True),
            ("git log --graph --oneline --all --decorate=short", "git log --decorate=short --all --oneline --graph", True),
            ("git log -n 2 --oneline", "git log --oneline -n 2", True),
            ("git log --oneline --max-count=2", "git log --max-count=2 --oneline", True),
            ("git log --oneline -2", "git log -2 --oneline", True),
            ("git log --oneline -n2", "git log -n2 --oneline", True),
            ("git log --oneline -n 2", "git log --max-count=2 --oneline", True),
            ("git log --oneline -n 2", "git log --oneline -n20", False),
            ("git log -n 2 --oneline", "git log -n --oneline 2", False),
            ("git log --oneline --format=full", "git log --format=full --oneline", False),
            ("git log --decorate=short --decorate=full", "git log --decorate=full --decorate=short", False),
            ("git log --oneline", "git --oneline log", False),
            ("git merge --no-edit feature/menu", "git merge feature/menu --no-edit", True),
            ('git commit -m "fix bug"', "git   commit -m 'fix bug'", True),
            ('git commit -m "fix  bug"', "git commit -m 'fix bug'", False),
            ('git commit -m "fix bug"', 'git -m commit "fix bug"', False),
            ('git commit -m "fix bug"', 'git commit -m "fix bug', False),
            ("git show -n 2 --format short", "git show --format 2 -n short", False),
            ("git add -- -f", "git add -f", False),
            ("git log --oneline", "git log --oneline; pwd", False),
            ("git status", "git\u3000status", False),
            ("git status", "\u00a0git status", False),
            ("git status", "git status\u00a0", False),
            ("git status", "git\vstatus", False),
            ("git status", "\tgit\tstatus\t", True),
        ]
        for n, (accepted, typed, expected) in enumerate(cases):
            with self.subTest(accepted=accepted, typed=typed):
                lesson = progress_tool.load_json(SUBJECTS)
                kp = next(k for k in lesson["knowledge_points"] if k["interaction_type"] == "terminal")
                lesson["knowledge_points"] = [kp]
                kp["items"] = [{"id": "command", "prompt": "输入命令", "commands": [
                    {"task": "执行指定操作", "accept": [accepted], "output": "done"}]}]
                page = self.open(_build(lesson, self.tmp.name, "terminal-equivalence-%d.html" % n))
                page.locator(".term-in").fill(typed)
                page.locator(".term-in").press("Enter")
                self.assertEqual(page.locator(".result.correct").count(), int(expected))
                self.assertEqual(page.locator(".term-log .err").count(), int(not expected))
                page.context.close()

    def test_works_when_storage_is_blocked(self):
        context = self.browser.new_context()
        self.addCleanup(context.close)
        context.add_init_script("Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked'); } });")
        page = context.new_page()
        page.set_default_timeout(5000)
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.goto(self.zh_url)
        page.locator(".flow input[type=text]").nth(1).fill("304")
        self.btn(page, "提交").click()
        self.btn(page, "确认").click()
        self.assertEqual(self.progress(page), "已作答 1 / 7 题")
        self.assertEqual(len(self.export_json(page)["attempts"]), 1)
        self.assertIn("当前环境无法在本地保存", page.locator("body").inner_text())
        self.assertEqual(errors, [])

    def test_bad_lesson_data_shows_an_error(self):
        path = os.path.join(self.tmp.name, "broken.html")
        with open(build_lesson.TEMPLATE, encoding="utf-8") as fh:
            html = build_lesson.DATA_BLOCK.sub(lambda m: m.group(1) + "{ nope" + m.group(3), fh.read())
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        context = self.browser.new_context()
        self.addCleanup(context.close)
        page = context.new_page()
        page.goto("file://" + path)
        self.assertIn("lesson data in this page could not be read", page.locator("body").inner_text())


if __name__ == "__main__":
    unittest.main()
