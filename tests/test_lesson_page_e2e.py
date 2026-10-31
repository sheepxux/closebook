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
