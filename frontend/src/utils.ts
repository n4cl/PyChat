export class Utils {
  // リクエストを送信する
  static request(
    url: string,
    method: string,
    data: null | string,
    readyStateChangeCallback: (xhr: XMLHttpRequest) => void,
  ) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
      readyStateChangeCallback(xhr);
    };
    xhr.send(data);
  }

  static getOriginalUrl() {
    const uri = new URL(window.location.href);
    return uri.origin;
  }

  static getEndpoint(path: string) {
    return this.getOriginalUrl() + path;
  }
}
