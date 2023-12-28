'use strict';

import { Utils } from "./utils.js";

(function () {

  function getUser(role, model) {
    // ユーザーを識別する
    let user = "Unknown";
    if (role === "user") {
      user = "You";
    } else {
      if (role === "assistant") {
        user = model;
      }
    }
    return user;
  }

  function removeHistory(count) {
    // リストの子要素を全て削除
    let history_list = document.getElementById("history_list");
    for (let i = 0; i < count; i++) {
      history_list.removeChild(history_list.children[0]);
    }
  }

  // レスポンスエリアをリフレッシュする
  function refleshResponseArea() {
    const main_content = document.getElementById("response_area");
    while (main_content.firstChild) {
      main_content.removeChild(main_content.firstChild);
    }
  }

  function refreshAttatchFile() {
    // モデルの data-attach_file の値で attach_file の表示を切り替える
    const model_select = document.getElementById("model_select");
    const is_attach_file = model_select.options[model_select.selectedIndex].dataset.attach_file
    const attach_file = document.getElementById("attach_file");
    if (is_attach_file === "0") {
      attach_file.classList.add("hidden");
    } else {
      attach_file.classList.remove("hidden");
    }
  }

  // レスポンスエリアにメッセージを追加する
  function generateResponseSection(message_id, message, role="Unknown") {
    let response_area = document.getElementById("response_area");
    response_area.dataset.message_id = message_id;
    const message_list = message.split("\n");

    const div_elm = document.createElement('div');
    div_elm.className = "mb-4";
    response_area.appendChild(div_elm);

    const role_elm = document.createElement('div');
    role_elm.className = "font-bold border-b-2 text-white mb-2";
    role_elm.textContent = role;
    div_elm.appendChild(role_elm);

    let p_elm = null;
    let sourcecode_area_elm = null;
    let pre_elm = null;
    let code_elm = null;
    let is_code_block = false;

    for (let i = 0; i < message_list.length; i++) {
      let row = message_list[i];

      if (is_code_block === false && row.startsWith("```")) {
        sourcecode_area_elm = document.createElement('div');
        sourcecode_area_elm.className = "rounded overflow-hidden";

        // p タグがあれば追加する
        if (p_elm !== null) {
          p_elm.className = "pb-2 text-white"
          div_elm.appendChild(p_elm);
          p_elm = null;
        }

        if (row.length > 3) {
          const lang_elm = document.createElement('div');
          lang_elm.className = "text-white bg-gray-700 p-2";
          lang_elm.textContent = row.slice(3);
          sourcecode_area_elm.appendChild(lang_elm);
        }

        is_code_block = true;
        pre_elm = document.createElement('pre');
        pre_elm.className = "bg-gray-800 p-2";
        code_elm = document.createElement('code');
        code_elm.className = "text-green-200";
        pre_elm.appendChild(code_elm);
        continue;
      }

      // コードブロックの中
      if (is_code_block === true) {
        // コードブロックの終了判定
        if (row === "```") {
          is_code_block = false;
          sourcecode_area_elm.appendChild(pre_elm);
          div_elm.appendChild(sourcecode_area_elm);
          continue;
        }
        code_elm.textContent += row + "\n";
        continue;
      }

      // 一般的なテキスト
      p_elm = document.createElement('p');
      p_elm.textContent = row;
      p_elm.className = "pb-2 text-white"
      div_elm.appendChild(p_elm);
    }
  }

  function fetchPastMessage(message_id) {
    // 履歴から選択したメッセージを取得する
    const path = "/app/chat/" + message_id;
    const url = Utils.getEndpoint(path);
    Utils.request(url, "GET", null, function (xhr) {
      // 過去のメッセージをレスポンスエリアに展開する
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)

        for (let i = 0; i < response.messages.length; i++) {
          let user = getUser(response.messages[i].role, response.messages[i].model);
          generateResponseSection(message_id, response.messages[i].content, user);
        }

      }
    });
  }

  function addHistory(message_id, message, is_first = false) {
    // リストに追加
    let history_list = document.getElementById("history_list");
    let new_li = document.createElement("li");
    new_li.className = "bg-gray-200 p-2 mr-1 rounded truncate hover:bg-gray-400";
    new_li.textContent = message;
    new_li.dataset.message_id = message_id;
    new_li.addEventListener("click", function () {
      refleshResponseArea()
      fetchPastMessage(this.dataset.message_id);
    });
    if (is_first) {
      history_list.prepend(new_li);
    } else {
      history_list.appendChild(new_li);
    }
  }

  // ボタンの有効か無効かを切り替える
  function toggleButton(id) {
    let button = document.getElementById(id);
    if (button.disabled) {
      button.disabled = false;
    } else {
      button.disabled = true;
    }
  }

  function getHistory() {
    const url = Utils.getEndpoint("/app/history")
    Utils.request(url, "GET", null, function (xhr) {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        for (let i = 0; i < response.history.length; i++) {
          addHistory(response.history[i].message_id, response.history[i].title);
        }
      }
    });
  }

  // 初期化
  (function initialize() {
    let history_list = document.getElementById("history_list");
    removeHistory(history_list.children.length);
    getHistory();
    refreshAttatchFile();
    refleshResponseArea();
  })();

  // モデル選択のイベントリスナーを登録
  const model_select = document.getElementById("model_select");
  model_select.addEventListener("change", function () {
    refreshAttatchFile();
  });

  // ボタンのイベントリスナーを登録
  let send_button = document.getElementById("send_button");
  send_button.addEventListener("click", function () {
    const response_area = document.getElementById("response_area");
    const _request = function(data) {
      Utils.request(url, "POST", data, function (xhr) {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
          const response = JSON.parse(xhr.responseText)

          // 新規チャットの場合
          if (response_area.dataset.message_id === "") {
            // TODO: 新規チャットのタイトルを取得する
            addHistory(response.message_id, query, true);
          }
          generateResponseSection(response.message_id, response.message, model);
        }
        toggleButton(send_button.id);
      });
    };

    let query_area = document.getElementById("query_area");
    if (query_area.value === "") {
      return;
    }
    toggleButton(this.id)

    // 問い合わせ結果の作成準備
    const query = query_area.value;
    let message_id = null;
    if (response_area.dataset.message_id === "") {
      generateResponseSection("", query, "You");
    } else {
      message_id = response_area.dataset.message_id;
      generateResponseSection(message_id, query, "You");
    }
    query_area.value = "";

    // リクエストbodyの作成
    let model_select = document.getElementById("model_select");
    const model = model_select.options[model_select.selectedIndex].value;

    const url = Utils.getEndpoint("/app/chat");
    let body = {query: query, model: model, message_id: message_id};
    const attach_file = document.getElementById("attach_file");
    if (attach_file.classList.contains("hidden") === false && attach_file.files.length > 0) {
      const reader = new FileReader();
      reader.onload = function() {
        body["file"] = reader.result;
        _request(JSON.stringify(body));
      };
      reader.readAsDataURL(attach_file.files[0]);
    } else {
      _request(JSON.stringify(body));
    }

  });

})();
