'use strict';
// console.log("JS print.js")
window.addEventListener("load", function() {
    // console.log("JS print.js");
    resizeText({
      elements: document.querySelectorAll('.fitText'),
      step: 0.2
    });
    resizeText({
      elements: document.querySelectorAll('.fitTextNameTrainer'),
      step: 0.5,
    });
    
});

const isOverflown = ({ clientHeight, scrollHeight }) => scrollHeight > clientHeight

const resizeText = ({ element, elements, minSize = 8, maxSize = 12, step = 1, unit = 'px' }) => {
  (elements || [element]).forEach(el => {
    let maxSize = el.getAttribute("size") || 12;
    let i = minSize;
    let overflow = false;
    const parent = el.parentNode;

    while (!overflow && i < maxSize) {
    // while (!overflow) {
        el.style.fontSize = `${i}${unit}`;
        overflow = isOverflown(parent);
      if (!overflow) i += step;
    }

    // revert to last state where no overflow happened
    el.style.fontSize = `${i - step}${unit}`;
  })
}


