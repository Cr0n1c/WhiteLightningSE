function CreateSessionID() {
    var result = '';
    var chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    for (var i = 20; i > 0; --i){
         result += chars[Math.floor(Math.random() * chars.length)];
    }

    return result;
}
