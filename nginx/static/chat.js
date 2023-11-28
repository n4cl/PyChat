'use strict';
(function () {
  function removeHistory(count) {
    // リストの子要素を全て削除
    let history_list = document.getElementById("history_list");
    for (let i = 0; i < count; i++) {
      history_list.removeChild(history_list.children[0]);
    }
  };

  function addHistory(message_id, message, is_first = false) {
    // リストに追加
    let history_list = document.getElementById("history_list");
    let new_li = document.createElement("li");
    new_li.className = "bg-gray-200 p-2 mr-1 rounded truncate hover:bg-gray-400";
    new_li.textContent = message;
    new_li.dataset.message_id = message_id;
    if (is_first) {
      history_list.prepend(new_li);
    } else {
      history_list.appendChild(new_li);
    }
  };

  // ボタンの有効か無効かを切り替える
  function toggleButton(id) {
    let button = document.getElementById(id);
    if (button.disabled) {
      button.disabled = false;
    } else {
      button.disabled = true;
    }
  };

  function getHistory() {
    const uri = new URL(window.location.href);
    let original_url = uri.origin;
    let url = original_url + "/app/history"
    request(url, "GET", null, function (xhr) {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        for (let i = 0; i < response.history.length; i++) {
          addHistory(response.history[i].message_id, response.history[i].title);
        }
      } else {
        console.log("error");
      }
    });
  }

  // リクエストを送信する
  function request(url, method, data, readyStateChangeCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
      readyStateChangeCallback(xhr);
    };
    xhr.send(data);
  };

  // 初期化
  (function initialize() {
    let history_list = document.getElementById("history_list");
    removeHistory(history_list.children.length);
    getHistory();
  })();


  // ボタンのイベントリスナーを登録
  let send_button = document.getElementById("send_button");
  send_button.addEventListener("click", function () {
    let query_area = document.getElementById("query_area");
    if (query_area.value === "") {
      return;
    };
    toggleButton(this.id)

    const generateResponseSection = function (message) {
      let response_area = document.getElementById("response_area");
      let response_div = document.createElement('div');
      response_div.innerText = message;
      response_div.className = "pb-2 text-white"
      response_area.appendChild(response_div);
    }
    // 問い合わせ結果の作成準備
    const query = query_area.value;
    generateResponseSection(query);
    query_area.value = "";


    // リクエストbodyの作成
    let model_select = document.getElementById("model_select");
    const model = model_select.options[model_select.selectedIndex].value;

    // 新規問い合わせの場合はmessage_idをnullにする
    let message_id_elm = document.getElementById("message_id");
    let message_id = null;
    if (message_id_elm.value !== "") {
      message_id = message_id_elm.value;
    }

    const uri = new URL(window.location.href);
    let original_url = uri.origin;
    let url = original_url + "/app/chat"
    let data = JSON.stringify({query: query, model: model, message_id: message_id});


    request(url, "POST", data, function (xhr) {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)

        // 新規チャットの場合
        if (message_id === null) {
          message_id_elm.value = response.message_id;
          addHistory(query, true);
        }
        generateResponseSection(response.message);

      } else {
        console.log("error");
      }
      toggleButton(send_button.id);
    });

  });



})();
