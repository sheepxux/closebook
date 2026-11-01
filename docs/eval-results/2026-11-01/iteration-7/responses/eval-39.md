# Eval 39 · 2026-11-01 round 7 (blind Codex run, three-level checking)

## Reply

用一道四选一辨析容易混淆的分支命令。请在题卡里选答案和把握程度，再检查；发送结果时需确认一次。

visualize{"path":"/private/tmp/claude-501/-Volumes-T7-Shield-closebook/055ba880-c52a-4427-b630-491016847e3b/scratchpad/eval-run-7/eval-39/workspace/work/git-branch-quiz.html"}

## Workspace changes

```json
{
 "work/git-branch-quiz.html": "created"
}
```

## Created file · work/git-branch-quiz.html

```html
<style>
.cb{font:16px/1.6 system-ui,sans-serif;max-width:640px;padding:20px;color:var(--text-primary,#202020)}.cb fieldset{border:0;padding:0;margin:16px 0}.cb label{display:block;padding:8px;border:1px solid #aaa;border-radius:7px;margin:7px 0;cursor:pointer}.cb button{font:inherit;padding:8px 16px;cursor:pointer}.cb button:disabled{opacity:.5;cursor:default}.cb code{font-size:15px}.cb .confidence label{display:inline-block;margin-right:6px}.cb [hidden]{display:none}
</style>
<section class="cb" aria-label="Git 分支命令诊断题">
<p>四选一 · 凭记忆作答；不知道也可以，本题只作诊断。</p>
<h3>你当前在 main 分支，工作区干净，且本地还没有 feature/login 分支。哪条命令会从当前提交创建 feature/login，并立即切换到它？</h3>
<fieldset id="answers"><legend>选择一个答案</legend>
<label><input type="radio" name="answer" value="A"> A. <code>git branch feature/login</code></label>
<label><input type="radio" name="answer" value="B"> B. <code>git switch feature/login</code></label>
<label><input type="radio" name="answer" value="C"> C. <code>git switch -c feature/login</code></label>
<label><input type="radio" name="answer" value="D"> D. <code>git branch -m feature/login</code></label>
<label><input type="radio" name="answer" value="dont_know"> 不知道</label>
</fieldset>
<fieldset class="confidence" id="confidence"><legend>把握程度</legend>
<label><input type="radio" name="confidence" value="1"> 1 · 猜的</label>
<label><input type="radio" name="confidence" value="2"> 2 · 比较确定</label>
<label><input type="radio" name="confidence" value="3"> 3 · 很确定</label>
</fieldset>
<button id="check" disabled>检查答案</button>
<div id="feedback" hidden aria-live="polite"><p id="verdict"></p>
<p>C 正确：<code>git switch -c feature/login</code> 创建新分支并切换过去。</p>
<ul><li>A：只创建分支，不切换。</li><li>B：切换到已有分支；题目中的目标分支尚不存在。</li><li>D：把当前分支改名，不是创建新分支。</li></ul>
<button id="send">完成并发送结果</button><p>点击后会弹出确认框；确认后结果才会发回聊天。</p>
<p id="status" role="status"></p></div>
</section>
<script>
(()=>{const q=s=>document.querySelector(s);let result,answer,confidence,sent=false;
document.querySelectorAll('input').forEach(i=>i.addEventListener('change',()=>{q('#check').disabled=!(q('input[name="answer"]:checked')&&q('input[name="confidence"]:checked'));}));
q('#check').addEventListener('click',()=>{answer=q('input[name="answer"]:checked')?.value;confidence=q('input[name="confidence"]:checked')?.value;if(!answer||!confidence)return;result=answer==='dont_know'?'dont_know':answer==='C'?'correct':'incorrect';q('#verdict').textContent=result==='correct'?'答对了。':result==='dont_know'?'已选择“不知道”，看看命令的区别。':'这次没选对，看看命令的区别。';q('#answers').disabled=true;q('#confidence').disabled=true;q('#check').disabled=true;q('#feedback').hidden=false;});
q('#send').addEventListener('click',async()=>{if(sent)return;sent=true;q('#send').disabled=true;const prompt=`closebook result · git-branch-create/git-branch-01 · ${answer} · ${result} · confidence ${confidence}`;try{await window.openai.sendFollowUpMessage({prompt,title:'提交 Git 分支题结果'});q('#status').textContent='请在确认框中确认发送。';}catch(e){q('#status').textContent='未能发送，请复制到聊天：'+prompt;}});
})();
</script>
```
