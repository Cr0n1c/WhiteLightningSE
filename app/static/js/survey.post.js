function PostData(data){
    var xhr;
     
    try {
      xhr = new XMLHttpRequest();
    } catch(e) {
      try {
        xhr = new ActiveXObject("Microsoft.XMLHTTP");
      } catch(e) {
        xhr = new ActiveXObject("MSXML2.ServerXMLHTTP");
      }
    }

    xhr.open('POST', 'survey_stage', true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send(data);
}
