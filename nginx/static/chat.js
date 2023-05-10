'use strict';
let req_button = document.getElementById("btn_request");
let inp_textarea = document.getElementById("input-text");

req_button.addEventListener("click", function() {
  const output = document.getElementById('output');
  const new_div = document.createElement('div');
  let text = inp_textarea.value;
  text = text.trim();
  if (text === '') {
    return;
  }
  new_div.textContent = text;
  output.appendChild(new_div);
});

inp_textarea.addEventListener("keypress", function(event) {
    if (event.code === "Enter") {
      req_button.click();
    }
});
