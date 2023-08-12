'use strict';
let req_button = document.getElementById("btn_request");
let inp_textarea = document.getElementById("input-text");

req_button.addEventListener("click", function() {
  let message = inp_textarea.value;
  message = message.trim();
  if (message === '') {
    return;
  }

  let mid_elm = document.getElementById("mid")
  let mid;
  if (mid_elm.value === "x") {
    mid = null;
  } else {
    mid = mid_elm.value;
  }

  let models_element = document.getElementById("models");
  let model = models_element.options[models_element.selectedIndex].value;
  const uri = new URL(window.location.href);
  const xhr = new XMLHttpRequest();
  let original_url = uri.origin
  let url = original_url + "/app/chat"
  let data = JSON.stringify({query: message, model: model, mid: mid});

  xhr.open("POST", url, true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  const status_elm = document.getElementById('status');

  xhr.onreadystatechange = function() {
    if(xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
      const query_div = document.createElement('div');
      query_div.className = "question";
      query_div.textContent = message;

      const answer_div = document.createElement('div');
      answer_div.className = "answer";
      const response = JSON.parse(xhr.responseText)
      let is_code = false;
      let pre_elm = null;
      for (const line of response.message.split("\n")) {
        if (line.startsWith("```") && line.charAt(3) !== "'") {
          // 文字列の先頭に ``` が存在し、その直後が ' 以外の場合の処理
          if (is_code === false) {
            // コードブロックの開始
            is_code = true;
            const new_pre = document.createElement('pre');
            pre_elm = new_pre;
            new_pre.textContent = line + "\n";
            answer_div.appendChild(new_pre);
          } else {
            is_code = false;
            pre_elm.textContent += line + "\n";
          }
        } else if (is_code === true) {
          // コードブロックの中の処理
          pre_elm.textContent += line + "\n";
        } else {
          // デフォルトの処理
          const p = document.createElement('p');
          p.className = "answer_child";
          if (line === "") {
            answer_div.appendChild(document.createElement('br'));
          } else {
            p.textContent = line;
          }
          answer_div.appendChild(p);
        }
      };

      if (typeof response.mid !== "undefined") {
        mid_elm.value = response.mid;
      } else {
        console.error("Cannot get mid from response.");
      }

      status_elm.textContent = "";
      status_elm.before(query_div);
      status_elm.before(answer_div);
      status_elm.hidden = true;
    } else {
      status_elm.textContent = "リクエストに失敗しました。"
    }
  }
  status_elm.textContent = "リクエスト実行中です。しばらくお待ちください。"
  status_elm.hidden = false;
  xhr.send(data);
});

inp_textarea.addEventListener("keypress", function(event) {
    if (event.shiftKey) {
      if (event.code === "Enter") {
        // keyup でのイベント発火時は改行が入っていない分とベースの高さ分を足す
        inp_textarea.rows = (inp_textarea.value.match(/\n/g) || []).length + 2;
        return;
      }
      return;
    }
    if (event.code === "Enter") {
      event.preventDefault();
      req_button.click();
      return;
    }
});

inp_textarea.addEventListener("keyup", function(event) {
  if (event.code === "Backspace") {
    inp_textarea.rows = (inp_textarea.value.match(/\n/g) || []).length + 1;
    return;
  }
});
