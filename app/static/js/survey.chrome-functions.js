chrome_plugins = "";
var count= 0;

function incrementCount(){
    count++;
}

function add(name) {
    chrome_plugins += ("&ch_id_"+ count + "=" + name).replace(/\s+/g, '-').toLowerCase();
    incrementCount();
}
