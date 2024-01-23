'use strict';

import { Utils } from "./utils.js";

(function () {

  function getUser(role: string, model: string) {
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

  function removeHistory(count: number) {
    // リストの子要素を全て削除
    const history_list = document.getElementById("history_list");
    if (history_list !== null) {
      for (let i = 0; i < count; i++) {
        history_list.removeChild(history_list.children[0]);
      }
    }
  }

  // レスポンスエリアをリフレッシュする
  function refleshResponseArea() {
    const main_content = document.getElementById("response_area");
    if (main_content !== null) {
      main_content.dataset.message_id = "";
      while (main_content.firstChild) {
        main_content.removeChild(main_content.firstChild);
      }
    }
  }

  function refreshAttatchFile() {
    // モデルの data-attach_file の値で attach_file の表示を切り替える
    const model_select = document.getElementById("model_select");
    // @ts-ignore
    const is_attach_file = model_select.options[model_select.selectedIndex].dataset.attach_file
    const attach_file = document.getElementById("attach_file");
    if (is_attach_file === "0") {
      // @ts-ignore
      attach_file.classList.add("hidden");
    } else {
      // @ts-ignore
      attach_file.classList.remove("hidden");
    }
  }

  // レスポンスエリアにメッセージを追加する
  function generateResponseSection(message_id: string, message: string, role="Unknown") {
    const response_area = document.getElementById("response_area");
    if (response_area === null) {
      console.error("response_area is null");
      return;
    }
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
      const row = message_list[i];

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
          // @ts-ignore
          sourcecode_area_elm.appendChild(pre_elm);
          // @ts-ignore
          div_elm.appendChild(sourcecode_area_elm);
          continue;
        }
        // @ts-ignore
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

  function fetchPastMessage(message_id: string) {
    // 履歴から選択したメッセージを取得する
    const path = "/app/chat/" + message_id;
    const url = Utils.getEndpoint(path);
    Utils.request(url, "GET", null, function (xhr) {
      // 過去のメッセージをレスポンスエリアに展開する
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)

        for (let i = 0; i < response.messages.length; i++) {
          const user = getUser(response.messages[i].role, response.messages[i].model);
          generateResponseSection(message_id, response.messages[i].content, user);
        }

      }
    });
  }
  class HistoryList {
    history_list: HTMLElement;
    default_li_class: string;
    default_div_class: string;
    default_button_class: string;

    constructor() {
      this.history_list = document.getElementById("history_list") as HTMLElement;
      this.default_li_class = "bg-gray-200 p-2 mr-1 rounded hover:bg-gray-400 flex flex-row";
      this.default_div_class = "truncate";
      this.default_button_class = "block hidden flex-none w-1/12";
      if (this.history_list === null) {
        throw new Error("history_list is null");
      }
    }

    public refreshHistoryList() {
      for (let i = 0; i < this.history_list.children.length; i++) {
        const _li = this.history_list.children[i]
        const _div = _li.children[0];
        const _button = _li.children[1];
        _li.className = this.default_li_class;
        _div.className = this.default_div_class;
        _button.className = this.default_button_class;
      }
      return;
    }

    public removeHistory(message_id: string) {
      for (let i = 0; i < this.history_list.children.length; i++) {
        const _li = this.history_list.children[i] as HTMLElement;
        if (_li.dataset.message_id === message_id) {
          this.history_list.removeChild(_li);
          return;
        }
      }
    }

    public addHistory(message_id: string, message: string, is_first = false) {

      const new_li = document.createElement("li");
      new_li.dataset.message_id = message_id;
      new_li.className = this.default_li_class;

      const new_title_div = document.createElement("div");
      new_title_div.className = this.default_div_class;
      new_title_div.textContent = message;
      new_li.appendChild(new_title_div);

      const message_option_button = document.createElement("button");
      message_option_button.innerText = "≡";
      message_option_button.className = this.default_button_class;
      new_li.appendChild(message_option_button);

      new_li.addEventListener("click", () => {
        // イベントリスナー内で this のコンテキストを維持するためにアロー関数を使用する

        // checked クラスがあれば何もしない
        if (new_li.classList.contains("checked")) {
          return;
        }

        const _message_id = new_li.dataset.message_id || "";
        if (new_li.dataset.message_id === "") {
          console.error("message_id is empty");
          return;
        }
        if (new_li.parentElement === null) {
          console.error("parentElement is null");
          return;
        }
        this.refreshHistoryList();

        new_li.className = "bg-gray-400 p-2 mr-1 rounded flex flex-row checked";
        new_title_div.className = "truncate flex-none w-11/12";
        message_option_button.classList.remove("hidden");
        new_li.appendChild(message_option_button);
        refleshResponseArea()
        fetchPastMessage(_message_id);
      });
      // チャットオプションのイベントリスナーを登録
      message_option_button.addEventListener("click", (event) => {
        event.stopPropagation(); // 親要素のイベントを発火させない
        const popup_menu = document.getElementById("popup_menu");
        if (popup_menu === null) {
          console.error("popup_menu is null");
          return;
        }
        popup_menu.style.top = `${event.clientY}px`;
        popup_menu.style.left = `${event.clientX}px`;
        popup_menu.classList.remove("hidden");
      });

      if (is_first) {
        this.history_list.prepend(new_li);
      } else {
        this.history_list.appendChild(new_li);
      }
    }
  }

  // ボタンの有効か無効かを切り替える
  function toggleButton(id: string) {
    const button = document.getElementById(id) as HTMLButtonElement;
    if (button === null) {
      console.error("button is null");
      return;
    }
    if (button.disabled) {
      button.disabled = false;
    } else {
      button.disabled = true;
    }
  }

  function generateHistoryList() {
    const url = Utils.getEndpoint("/app/history")
    const history_list = new HistoryList();
    Utils.request(url, "GET", null, function (xhr) {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        for (let i = 0; i < response.history.length; i++) {
          history_list.addHistory(response.history[i].message_id, response.history[i].title);
        }
      }
    });
  }

  // 初期化
  (function initialize() {
    const history_list = document.getElementById("history_list");
    if (history_list) {
      removeHistory(history_list.children.length);
      generateHistoryList();
    }
    refreshAttatchFile();
    refleshResponseArea();
  })();

  // 履歴の削除
  const delete_history = document.getElementById("delete_history");
  delete_history?.addEventListener("click", function () {
    const popup_menu = document.getElementById("popup_menu");
    if (popup_menu === null) {
      console.error("popup_menu is null");
      return;
    }
    const history_list = new HistoryList();
    const response_area = document.getElementById("response_area");
    if (response_area === null) {
      console.error("response_area is null");
      return;
    }
    const _message_id = response_area.dataset.message_id;
    if (_message_id === "" || _message_id === undefined) {
      console.error("_message_id is empty");
      return;
    }
    let url = Utils.getEndpoint("/app/chat");
    url += "/" + _message_id;
    Utils.request(url, "DELETE", null, function (xhr) {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        history_list.refreshHistoryList();
        history_list.removeHistory(_message_id);
      }
    });
    popup_menu.classList.add("hidden");
    refleshResponseArea();
  });

  // モデル選択のイベントリスナーを登録
  const model_select = document.getElementById("model_select");
  if (model_select) {
    model_select.addEventListener("change", function () {
      refreshAttatchFile();
    });
  }

  // ボタンのイベントリスナーを登録
  const send_button = document.getElementById("send_button");
  if (send_button === null) {
    console.error("send_button is null");
    return;
  }
  send_button.addEventListener("click", function () {
    const response_area = document.getElementById("response_area");
    if (response_area === null) {
      console.error("response_area is null");
      return;
    }
    const history_list = new HistoryList();
    const _request = function(data: string) {
      Utils.request(url, "POST", data, function (xhr) {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
          const response = JSON.parse(xhr.responseText)

          // 新規チャットの場合
          if (response_area.dataset.message_id === "") {
            // TODO: 新規チャットのタイトルを取得する
            history_list.addHistory(response.message_id, query, true);
          }
          generateResponseSection(response.message_id, response.message, model);
        }
        toggleButton(send_button.id);
      });
    };

    const query_area = document.getElementById("query_area") as HTMLTextAreaElement;
    if (query_area && query_area.value === "") {
      return;
    }
    toggleButton(this.id)

    // 問い合わせ結果の作成準備
    const query = query_area.value;
    let message_id = null;
    // @ts-ignore
    if (response_area.dataset.message_id === "") {
      generateResponseSection("", query, "You");
    } else {
      // @ts-ignore
      message_id = response_area.dataset.message_id;
      // @ts-ignore
      generateResponseSection(message_id, query, "You");
    }
    query_area.value = "";

    // リクエストbodyの作成
    const model_select = document.getElementById("model_select");
    // @ts-ignore
    const model = model_select.options[model_select.selectedIndex].value;

    const url = Utils.getEndpoint("/app/chat");
    const body = {query: query, model: model, message_id: message_id};
    const attach_file = document.getElementById("attach_file");
    // @ts-ignore
    if (attach_file.classList.contains("hidden") === false && attach_file.files.length > 0) {
      const reader = new FileReader();
      reader.onload = function() {
        // @ts-ignore
        body["file"] = reader.result;
        _request(JSON.stringify(body));
      };
      // @ts-ignore
      reader.readAsDataURL(attach_file.files[0]);
    } else {
      _request(JSON.stringify(body));
    }

  });

  const document_body = document.getElementById("body");
  if (document_body) {
    const popup_menu = document.getElementById("popup_menu");
    if (popup_menu === null) {
      console.error("popup_menu is null");
      return;
    }
    document_body.addEventListener("click", function () {
      // ポップアップメニューを非表示にする
      if (popup_menu.classList.contains("hidden") === false) {
        popup_menu.classList.add("hidden");
      }
    });
  } else {
    console.error("document_body is null");
  }

  const new_chat_button = document.getElementById("new_chat_button");
  new_chat_button?.addEventListener("click", function () {
    const history_list = new HistoryList();
    history_list.refreshHistoryList();
    refleshResponseArea();
  });

})();
