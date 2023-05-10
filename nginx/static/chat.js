'use strict';
let req_button = document.getElementById("btn_request");
let inp_textarea = document.getElementById("input-text");

req_button.addEventListener("click", function() {
  let message = inp_textarea.value;
  message = message.trim();
  if (message === '') {
    return;
  }
  let models_element = document.getElementById("models");
  let model = models_element.options[models_element.selectedIndex].value;
  const uri = new URL(window.location.href);
  const xhr = new XMLHttpRequest();
  let original_url = uri.origin
  let url = original_url + "/app/chat"
  let data = JSON.stringify({query: message, model: model});

  xhr.open("POST", url, true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  const output = document.getElementById('output');
  const new_div = document.createElement('div');

  xhr.onreadystatechange = function() {
    if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
      new_div.textContent = xhr.responseText;
      output.appendChild(new_div);
    }
  }
  new_div.value = "リクエスト実行中です。しばらくお待ちください。"
  xhr.send(data);
});

inp_textarea.addEventListener("keypress", function(event) {
    if (event.code === "Enter") {
      req_button.click();
    }
});
