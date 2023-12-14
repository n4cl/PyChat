export class Utils {

  // リクエストを送信する
  static request(url, method, data, readyStateChangeCallback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
      readyStateChangeCallback(xhr);
    };
    xhr.send(data);
  }

  static getOriginlUrl() {
    const uri = new URL(window.location.href);
    return uri.origin;
  }

  static getEndpoint(path) {
    return this.getOriginlUrl() + path;
  }

}
