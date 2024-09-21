"use strict";

import { Utils } from "./utils.js";
import { ElementValidator } from "./utils.js";

(function () {
  const model_select = ElementValidator.getElementByIdOrThrow<HTMLSelectElement>("model_select");
  const history_list_elm = ElementValidator.getElementByIdOrThrow<HTMLElement>("history_list");
  const attach_file = ElementValidator.getElementByIdOrThrow<HTMLInputElement>("attach_file");
  const response_area = ElementValidator.getElementByIdOrThrow<HTMLElement>("response_area");
  const new_chat_button = ElementValidator.getElementByIdOrThrow<HTMLButtonElement>("new_chat_button");
  const document_body = ElementValidator.getElementByIdOrThrow<HTMLElement>("body");
  const send_button = ElementValidator.getElementByIdOrThrow<HTMLButtonElement>("send_button");
  const query_area = ElementValidator.getElementByIdOrThrow<HTMLTextAreaElement>("query_area");
  const popup_menu = ElementValidator.getElementByIdOrThrow<HTMLElement>("popup_menu");
  const delete_history = ElementValidator.getElementByIdOrThrow<HTMLButtonElement>("delete_history");

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
    if (history_list_elm !== null) {
      for (let i = 0; i < count; i++) {
        history_list_elm.removeChild(history_list_elm.children[0]);
      }
    }
  }

  // レスポンスエリアをリフレッシュする
  function refleshResponseArea() {
    if (response_area !== null) {
      response_area.dataset.message_id = "";
      while (response_area.firstChild) {
        response_area.removeChild(response_area.firstChild);
      }
    }
  }

  function refreshAttatchFile() {
    // モデルの data-attach_file の値で attach_file の表示を切り替える
    const is_attach_file = model_select.options[model_select.selectedIndex].dataset.attach_file;
    if (is_attach_file === "0") {
      attach_file.classList.add("hidden");
    } else {
      attach_file.classList.remove("hidden");
    }
  }

  // テキストエリアの高さを調整する
  function adjustHeight(elm: HTMLTextAreaElement) {
    elm.style.height = "auto";
    elm.style.height = elm.scrollHeight + "px";
  }

  // バックエンドからモデルの取得
  function fetchModel() {
    const url = Utils.getEndpoint("/app/models");
    Utils.request(url, "GET", null, function (xhr) {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        // 初期のモデルを削除する
        while (model_select.firstChild) {
          model_select.removeChild(model_select.firstChild);
        }
        // モデルを追加する
        for (let i = 0; i < response.models.length; i++) {
          const option = document.createElement("option");
          option.value = response.models[i].id;
          option.textContent = response.models[i].name;
          model_select.appendChild(option);
        }
      }
    });
  }

  // レスポンスエリアにメッセージを追加する
  function generateResponseSection(
    message: string,
    role: string = "Unknown",
    create_date: string = "",
  ) {
    // create_date が空の場合は現在時刻を取得する
    if (create_date === "") {
      const date = new Date();
      create_date = date.toLocaleString();
    }

    const message_list = message.split("\n");

    const div_elm = document.createElement("div");
    div_elm.className = "mb-4";
    response_area.appendChild(div_elm);

    const title_elm = document.createElement("div");
    title_elm.className = "border-b-2 text-white mb-2";
    const role_elm = document.createElement("span");
    role_elm.textContent = role;
    role_elm.className = "font-bold";
    const create_date_elm = document.createElement("span");
    create_date_elm.textContent = ": " + create_date;
    title_elm.appendChild(role_elm);
    title_elm.appendChild(create_date_elm);
    div_elm.appendChild(title_elm);

    let p_elm = null;
    let sourcecode_area_elm = document.createElement("div");
    let pre_elm = document.createElement("pre");
    let code_elm = null;
    let is_code_block = false;

    for (let i = 0; i < message_list.length; i++) {
      const row = message_list[i];

      if (is_code_block === false && row.startsWith("```")) {
        sourcecode_area_elm = document.createElement("div");
        sourcecode_area_elm.className = "rounded overflow-hidden";

        // p タグがあれば追加する
        if (p_elm !== null) {
          p_elm.className = "pb-2 text-white";
          div_elm.appendChild(p_elm);
          p_elm = null;
        }

        if (row.length > 3) {
          const lang_elm = document.createElement("div");
          lang_elm.className = "text-white bg-gray-700 p-2";
          lang_elm.textContent = row.slice(3);
          sourcecode_area_elm.appendChild(lang_elm);
        }

        is_code_block = true;
        pre_elm = document.createElement("pre");
        pre_elm.className = "bg-gray-800 p-2";
        code_elm = document.createElement("code");
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
          // 必要に応じてスクロールバーを追加する
          if (pre_elm.scrollWidth > pre_elm.clientWidth) {
            pre_elm.classList.add("overflow-x-scroll");
          }
          continue;
        }
        if (code_elm !== null) {
          code_elm.textContent += row + "\n";
          continue;
        }
      }

      // 一般的なテキスト
      p_elm = document.createElement("p");
      p_elm.textContent = row;
      p_elm.className = "pb-2 text-white";
      div_elm.appendChild(p_elm);
    }
  }

  function fetchPastMessage(message_id: string) {
    // 履歴から選択したメッセージを取得する
    const path = "/app/messages/" + message_id;
    const url = Utils.getEndpoint(path);
    Utils.request(url, "GET", null, function (xhr) {
      // 過去のメッセージをレスポンスエリアに展開する
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);

        for (let i = 0; i < response.messages.length; i++) {
          const user = getUser(response.messages[i].role, response.messages[i].model);
          generateResponseSection(response.messages[i].content, user, response.messages[i].create_date);
        }
        response_area.dataset.message_id = message_id;
      }
    });
  }
  class HistoryList {
    history_list: HTMLElement;
    default_li_class: string;
    default_div_class: string;
    default_button_class: string;

    constructor() {
      this.history_list = history_list_elm;
      this.default_li_class = "bg-gray-200 p-2 mr-1 rounded hover:bg-gray-400 flex flex-row";
      this.default_div_class = "truncate";
      this.default_button_class = "block hidden flex-none w-1/12";
      if (this.history_list === null) {
        throw new Error("history_list is null");
      }
    }

    public refreshHistoryList() {
      for (let i = 0; i < this.history_list.children.length; i++) {
        const _li = this.history_list.children[i];
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
        refleshResponseArea();
        fetchPastMessage(_message_id);
      });
      // チャットオプションのイベントリスナーを登録
      message_option_button.addEventListener("click", (event) => {
        event.stopPropagation(); // 親要素のイベントを発火させない

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
    const button = ElementValidator.getElementByIdOrThrow<HTMLButtonElement>(id);
    if (button.disabled) {
      button.disabled = false;
    } else {
      button.disabled = true;
    }
  }

  function generateHistoryList() {
    let url = Utils.getEndpoint("/app/messages");
    url += "?page_size=40";
    const history_list = new HistoryList();
    Utils.request(url, "GET", null, function (xhr) {
      if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        for (let i = 0; i < response.history.length; i++) {
          history_list.addHistory(response.history[i].message_id, response.history[i].title);
        }
      }
    });
  }

  function addChatToResponseArea(query: string) {
    request_chat(query).then((response_from_llm) => {
      if (response_from_llm === null) {
        // TODO: 失敗した場合はモーダルでエラーを表示しても良いかもしれない
        return;
      }
      const model_name = model_select.options[model_select.selectedIndex].textContent ?? "Unknown" as string;
      generateResponseSection(response_from_llm, model_name);
    });
  }

  async function request_chat(query: string) {
    const model_id = model_select.options[model_select.selectedIndex].value;
    const post_chat_response = await fetch(Utils.getEndpoint("/app/messages/" + response_area.dataset.message_id + "/chat"),
                                            {"method": "POST",
                                             "headers": {"Content-Type": "application/json"},
                                             "body": JSON.stringify({"llm_model_id": model_id,
                                                                     "query": query})});
    if (!post_chat_response.ok) {
      console.error("Failed to post chat");
      return null;
    }
    // レスポンスの json の message を返す
    return post_chat_response.json().then((response) => {
      return response.message;
    });
  }

  async function addMessageToResponseArea(query: string) {

    async function generateAndSaveTitle(query: string, message_id: string) {
      try {
        // タイトル生成
        const title = await generateTitle(query);

        // メッセージの更新
        await updateMessage(message_id, title);

        // 履歴の追加
        const historyList = new HistoryList();
        historyList.addHistory(message_id, title, true);

      } catch (error) {
        console.error("Error in generateAndSaveTitle:", error);
      }
    }

    async function generateTitle(query: string) {
      const response = await fetch(Utils.getEndpoint("/app/generate/title"), {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({query})
      });

      if (!response.ok) {
        throw new Error("Failed to generate title");
      }

      const data = await response.json();
      return data.title;
    }

    async function updateMessage(message_id: string, title: string) {
      const response = await fetch(Utils.getEndpoint(`/app/messages/${message_id}`), {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({title})
      });

      if (!response.ok) {
        throw new Error("Failed to update message");
      }
    }

    // message のリソースを作成する
    const post_message_response = await fetch(Utils.getEndpoint("/app/messages"),
                                             {"method": "POST",
                                              "headers": {"Content-Type": "application/json"},
                                              "body": JSON.stringify({"title": query})});
    if (!post_message_response.ok) {
      console.error("Failed to post message");
      return;
    }
    let message_id = "";
    await post_message_response.json().then((response) => {
      message_id = response.message_id;
      response_area.dataset.message_id = message_id;
    });

    addChatToResponseArea(query);
    generateAndSaveTitle(query, message_id);
  }

  // 初期化
  (function initialize() {
    if (history_list_elm) {
      removeHistory(history_list_elm.children.length);
      generateHistoryList();
    }
    fetchModel();
    refreshAttatchFile();
    refleshResponseArea();
  })();

  // 履歴の削除
  delete_history?.addEventListener("click", function () {
    const history_list = new HistoryList();
    const _message_id = response_area.dataset.message_id;
    if (_message_id === "" || _message_id === undefined) {
      console.error("_message_id is empty");
      return;
    }
    let url = Utils.getEndpoint("/app/messages");
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
  if (model_select) {
    model_select.addEventListener("change", function () {
      refreshAttatchFile();
    });
  }

  // 入力フォームのイベントリスナーを登録
  adjustHeight(query_area);
  query_area.addEventListener("input", () => adjustHeight(query_area));

  // ボタンのイベントリスナーを登録
  send_button.addEventListener("click", function () {

    if (query_area && query_area.value.trim() === "") {
      return;
    }
    toggleButton(send_button.id);

    // ユーザーのメッセージをレスポンスエリアに追加する
    generateResponseSection(query_area.value, "You");

    const message_id = response_area.dataset.message_id as string;
    if (message_id === "") {
      // 新規メッセージ
      addMessageToResponseArea(query_area.value);
    } else {
      addChatToResponseArea(query_area.value);
    }
    query_area.value = "";
    adjustHeight(query_area);
    toggleButton(this.id);
  });

  document_body.addEventListener("click", function () {
    // ポップアップメニューを非表示にする
    if (popup_menu.classList.contains("hidden") === false) {
      popup_menu.classList.add("hidden");
    }
  });

  new_chat_button?.addEventListener("click", function () {
    const history_list = new HistoryList();
    history_list.refreshHistoryList();
    refleshResponseArea();
  });
})();
