// Shared quiz widget. Markup:
//
//   <div class="quiz" data-answer="2">        <!-- zero-based index of the right button -->
//     <p class="q">Question?</p>
//     <button>option</button> ...             <!-- keep options the same word count -->
//     <p class="why" hidden>Shown after answering.</p>
//   </div>
//
//   <div class="recall">                      <!-- free-text retrieval, self-checked -->
//     <p class="q">Prompt?</p>
//     <textarea></textarea>
//     <details><summary>Model answer</summary>...</details>
//   </div>
//
//   <p id="score"></p>                        <!-- filled once every quiz is answered -->
//
// First click locks a quiz, marks right and wrong, reveals the explanation.
// The score line names the option picked on each miss (A, B, C...) and carries
// whatever was typed into each recall box, so the teacher can see both.
document.addEventListener('DOMContentLoaded', () => {
  const quizzes = [...document.querySelectorAll('.quiz')];
  const recalls = [...document.querySelectorAll('.recall textarea')];
  const results = [];
  quizzes.forEach((quiz, i) => {
    const buttons = [...quiz.querySelectorAll('button')];
    const answer = Number(quiz.dataset.answer);
    buttons.forEach((button, picked) => {
      button.addEventListener('click', () => {
        buttons.forEach(b => (b.disabled = true));
        buttons[answer].classList.add('right');
        if (picked !== answer) button.classList.add('wrong');
        const why = quiz.querySelector('.why');
        if (why) why.hidden = false;
        results[i] = { ok: picked === answer, picked };
        showScore();
      });
    });
  });
  recalls.forEach(box => box.addEventListener('input', showScore));
  function showScore() {
    const score = document.getElementById('score');
    const answered = results.filter(Boolean);
    if (!score || answered.length < quizzes.length) return;
    const summary = results
      .map((r, i) => `Q${i + 1} ${r.ok ? 'right' : `missed (picked ${'ABCDEF'[r.picked]})`}`)
      .join(', ');
    const written = recalls
      .map((box, i) => ` | Written ${i + 1}: ${box.value.trim() || '(blank)'}`)
      .join('');
    score.textContent = `You got ${answered.filter(r => r.ok).length} of ${quizzes.length}. ` +
      'Paste this line back to your teacher so the next lesson is pitched right:';
    const line = document.createElement('code');
    line.textContent = `${document.title}: ${summary}${written}`;
    score.append(line);
  }
});
