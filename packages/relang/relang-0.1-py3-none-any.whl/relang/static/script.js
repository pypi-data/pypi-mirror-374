const sourceLang = document.getElementById('source-lang');
const targetLang = document.getElementById('target-lang');
const sourceText = document.getElementById('source-text');
const targetText = document.getElementById('target-text');

sourceText.addEventListener('input', (e) => {
    targetText.textContent = '';
});

let dir = (s) => (s.endsWith('_Arab') | s.endsWith('_Hebr')) ? "rtl" : "ltr";

sourceLang.addEventListener('change', (e) => {
    sourceText.dir = dir(e.target.value);
    targetText.textContent = '';
});

targetLang.addEventListener('change', (e) => {
    targetText.dir = dir(e.target.value);
    targetText.textContent = '';
});

targetText.addEventListener('click', async (e) => {
    if (e.target.textContent) return;
    e.target.textContent = 'Waiting for translation to start ...';
    const response = await fetch("/translate", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({src_text: sourceText.value, src_lang: sourceLang.value, tgt_lang: targetLang.value}),
    });
    const decoder = new TextDecoder();
    const reader = response.body.getReader();
    let text = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      text += decoder.decode(value);
      e.target.textContent = text + "(still translating)";
    }
    e.target.textContent = text;
});
