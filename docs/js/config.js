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

// Instant navigation swaps the page without loading MathJax again
document$.subscribe(() => {
  if (typeof MathJax.typesetPromise !== "function") {
    return;
  }
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});
