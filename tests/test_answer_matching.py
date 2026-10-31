"""Exercise the shipped JavaScript graders and submit callbacks without a browser.

Node's VM runs functions extracted from the template. The tiny view stub below
only builds callback-bearing nodes; it does not simulate browser rendering.
"""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "skills/closebook/assets/lesson-template.html"
NODE = shutil.which("node")

HARNESS = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const request = JSON.parse(fs.readFileSync(0, 'utf8'));
const html = fs.readFileSync(request.template, 'utf8');
const names = ['norm', 'matches', 'normCode', 'matchesCode', 'blankCheck',
  'clozeModel', 'normCmd', 'cmdWords', 'cmdShape', 'sameCmd', 'renderPlainQa',
  'appendBlankControls'];
const source = names.map(name => {
  const start = html.indexOf('  function ' + name + '(');
  assert.notEqual(start, -1, name);
  const end = html.indexOf('\n  function ', start + 1);
  return html.slice(start, end < 0 ? undefined : end);
}).join('\n');
const sandbox = {
  assert,
  lang: {id: 'english', knowledge_type: 'language_production'},
  code: {id: 'python', knowledge_type: 'procedural'},
  T: new Proxy({}, {get: (_, key) => String(key)}),
  h: (tag, attrs, ...children) => ({tag, attrs, children}),
  rich: x => x,
  codeBlock: () => null,
  isContested: () => false,
  confidenceField: () => null,
  hintBlock: () => null,
  durationSince: () => 1,
  formatOf: (_, format) => format,
  addAttempt: (_, id, attempt) => ({id, ...attempt}),
};
vm.createContext(sandbox);
vm.runInContext(source + '\n' + request.check, sandbox, {timeout: 2000});
"""


@unittest.skipUnless(NODE, "Node.js is required for template JavaScript tests")
class AnswerMatching(unittest.TestCase):
    def check_js(self, check):
        result = subprocess.run(
            [NODE, "-e", HARNESS],
            input=json.dumps({"template": str(TEMPLATE), "check": check}),
            capture_output=True, text=True, timeout=5,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_language_contractions_accept_typographic_apostrophes(self):
        self.check_js(r"""
          for (const apostrophe of ["'", '\u2018', '\u2019', '\u0060', '\u02bc']) {
            for (const [typed, expected] of [
              [apostrophe + 've known', "'ve known"],
              [apostrophe + 's not seen', "'s not seen"],
              ['hasn' + apostrophe + 't seen', "hasn't seen"],
              ['I' + apostrophe + 've known her.', "I've known her"],
            ]) {
              assert.equal(matches(typed, [expected], false, lang), true, typed);
              assert.equal(matches(expected, [typed], false, lang), true, typed);
            }
          }
          assert.equal(matches('‘VE KNOWN', ["'ve known"], true, lang), false);
        """)

    def test_typography_does_not_forgive_grammar_or_missing_apostrophes(self):
        self.check_js(r"""
          const accept = ["has not seen", "hasn't seen", "'s not seen"];
          for (const wrong of ['hasnt seen', 'has not saw', 'didn’t see', 's not seen'])
            assert.equal(matches(wrong, accept, false, lang), false, wrong);
          assert.equal(matches('has moved', ['moved', 'did move'], false, lang), false);
          assert.equal(matches('I‘ve known', ["have known", "'ve known"], false, lang), false);
          assert.equal(matches('‘ve  known', ["'ve known"], false, lang), true);
        """)

    def test_cloze_submit_uses_language_normalization_without_manual_marks(self):
        self.check_js(r"""
          const model = clozeModel("I [[have known|'ve known]] her. She [[moved|did move]]. She [[has not seen|'s not seen|hasn't seen]] him.");
          for (const apostrophe of ["'", '‘', '’', '`', 'ʼ']) {
            const ui = {vals: [apostrophe + 've known', 'moved', apostrophe + 's not seen']};
            const out = [];
            appendBlankControls(out, lang, {id: 'story', prompt: 'Fill'}, ui, () => {}, model.cells, 'cloze', 'cloze_passage');
            const submit = out[0].children.find(node => node && node.tag === 'button');
            submit.attrs.onclick();
            assert.equal(ui.checked, true);
            assert.equal(ui.auto.every(Boolean), true);
            assert.equal(ui.marks.every(Boolean), true);
            assert.equal(ui.vals[0], apostrophe + 've known', 'preserve raw learner input');
          }
          const wrong = {vals: ['‘ve known', 'has moved', '‘s not seen']};
          blankCheck(wrong, model.cells, lang);
          assert.equal(JSON.stringify(wrong.auto), '[true,false,true]');
        """)

    def test_plain_qa_submit_uses_language_normalization(self):
        self.check_js(r"""
          const item = {id: 'duration', question: 'I ___ her (know).', answer: 'have known', accept: ['have known', "'ve known"]};
          for (const [kp, typed, expected] of [[lang, '‘ve known', 'correct'], [code, '‘ve known', 'incorrect'], [lang, 've known', 'incorrect']]) {
            const ui = {draft: typed, conf: 2};
            const out = renderPlainQa(kp, item, item, ui, () => {}, 'plain_qa');
            out.find(node => node && node.tag === 'form').attrs.onsubmit({preventDefault() {}});
            assert.equal(ui.result, expected);
            assert.equal(ui.answerText, typed);
          }
        """)

    def test_code_and_commands_keep_apostrophes_literal(self):
        self.check_js(r"""
          for (const apostrophe of ['‘', '’', '`', 'ʼ']) {
            assert.equal(matches(apostrophe + 've known', ["'ve known"], false, code), false);
            assert.equal(matchesCode(apostrophe + 've known', ["'ve known"]), false);
            assert.equal(matchesCode('["a' + apostrophe + 'b"]', ['["a\'b"]'], 'container'), false);
            assert.equal(sameCmd('git commit -m "a' + apostrophe + 'b"', 'git commit -m "a\'b"'), false);
          }
          const ui = {vals: ['‘ve known']};
          blankCheck(ui, [{code: true, text: "'ve known"}], lang);
          assert.equal(ui.auto[0], false, 'code cells remain literal even on a language point');
        """)


if __name__ == '__main__':
    unittest.main()
