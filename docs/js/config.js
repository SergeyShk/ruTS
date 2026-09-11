window.MathJax = {
    tex: {
      inlineMath: [["\\(", "\\)"]],
      displayMath: [["\\[", "\\]"]],
      processEscapes: true,
      processEnvironments: true
    },
    options: {
      ignoreHtmlClass: ".*|",
      processHtmlClass: "arithmatex"
    }
  };

// Повторный рендеринг формул при instant-навигации Material for MkDocs.
// При первой загрузке страницы MathJax рендерит формулы сам, поэтому первое событие пропускается
let initialLoad = true;
document$.subscribe(() => {
  if (initialLoad) {
    initialLoad = false;
    return;
  }
  if (typeof MathJax.typesetPromise === "function") {
    MathJax.typesetClear();
    MathJax.texReset();
    MathJax.typesetPromise();
  }
});
