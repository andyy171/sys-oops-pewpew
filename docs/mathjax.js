window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\(', '\\)']],
    displayMath: [['$$', '$$'], ['\\[', '\\]']],
    processEscapes: true,
    packages: {'[+]': ['textmacros']}
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
  }
};
