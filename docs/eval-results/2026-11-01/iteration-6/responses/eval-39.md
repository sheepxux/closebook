# Eval 39 · 2026-11-01 round 6 (blind Codex run, in-widget checking)

## Reply

只考一道，用闭卷辨析检查易混命令。选答案和把握程度后，题卡会当场判定；提交结果时需再确认一次。

visualize{"path":"/private/tmp/claude-501/-Volumes-T7-Shield-closebook/055ba880-c52a-4427-b630-491016847e3b/scratchpad/eval-run-6/eval-39/workspace/work/git-branch-quiz.html"}

## Workspace changes

```json
{
 "work/git-branch-quiz.html": "created"
}
```

## Created file · work/git-branch-quiz.html

```html
<section id="git-quiz" lang="zh-CN">
<style>
#git-quiz{font:16px/1.6 system-ui,sans-serif;max-width:680px;padding:20px;color:inherit}#git-quiz fieldset{border:0;padding:0;margin:18px 0}#git-quiz label{display:block;padding:8px;border:1px solid #9996;border-radius:7px;margin:7px 0;cursor:pointer}#git-quiz button{font:inherit;padding:8px 16px;cursor:pointer}#git-quiz button:disabled{cursor:default;opacity:.55}#git-quiz code{font-size:15px}#git-quiz .muted{font-size:14px}#git-quiz [hidden]{display:none}
</style>
<p class="muted">闭卷辨析 · Git 分支命令 · 诊断题，不计错题</p>
<p><strong>当前在 <code>main</code> 分支，工作区干净，本地和远程都没有名为 <code>feature/login</code> 的分支。下面哪条命令会从当前提交创建这个分支，并立即切换过去？</strong></p>
<form>
<fieldset id="answers"><legend>选择一个答案</legend>
<label><input type="radio" name="answer" value="A"> A. <code>git branch feature/login</code></label>
<label><input type="radio" name="answer" value="B"> B. <code>git switch feature/login</code></label>
<label><input type="radio" name="answer" value="C"> C. <code>git switch -c feature/login</code></label>
<label><input type="radio" name="answer" value="D"> D. <code>git branch -m feature/login</code></label>
<label><input type="radio" name="answer" value="dont_know"> 不知道</label>
</fieldset>
<fieldset id="confidence"><legend>把握程度</legend>
<label><input type="radio" name="confidence" value="1"> 1 · 猜的</label>
<label><input type="radio" name="confidence" value="2"> 2 · 有些把握</label>
<label><input type="radio" name="confidence" value="3"> 3 · 很确定</label>
</fieldset>
<button id="check" type="submit" disabled>检查答案</button>
</form>
<div id="feedback" aria-live="polite" hidden><p id="verdict"></p><p>A：只创建分支，不切换。B：切换到已有分支；题设中的分支不存在。C：创建新分支并切换，符合要求。D：重命名当前分支，并不是新建分支。</p><button id="send" type="button">提交结果</button><p class="muted">提交后还需在应用弹窗中确认，结果才会发回聊天。</p></div>
<script>
(()=>{const root=document.getElementById('git-quiz'),form=root.querySelector('form'),check=root.querySelector('#check'),send=root.querySelector('#send');let resultLine='',locked=false;const chosen=n=>form.querySelector('input[name="'+n+'"]:checked')?.value;form.addEventListener('change',()=>{check.disabled=locked||!chosen('answer')||!chosen('confidence')});form.addEventListener('submit',e=>{e.preventDefault();if(locked||!chosen('answer')||!chosen('confidence'))return;const answer=chosen('answer'),confidence=chosen('confidence'),result=answer==='dont_know'?'dont_know':answer==='C'?'correct':'incorrect';locked=true;root.querySelector('#answers').disabled=true;root.querySelector('#confidence').disabled=true;check.disabled=true;root.querySelector('#verdict').textContent=result==='correct'?'答对了。':result==='dont_know'?'这次选择了“不知道”。正确答案是 C。':'这次未选对。正确答案是 C。';root.querySelector('#feedback').hidden=false;resultLine='closebook result · git-branch-create-switch/q1 · '+answer+' · '+result+' · confidence '+confidence;});send.addEventListener('click',()=>{send.disabled=true;window.openai.sendFollowUpMessage({prompt:resultLine,title:'提交本题结果'});});})();
</script>
</section>
```
