var getIPs = function (callback){
var ip_dups = {};

var RTCPeerConnection = window.RTCPeerConnection
                     || window.mozRTCPeerConnection
                     || window.webkitRTCPeerConnection;
var useWebKit = !!window.webkitRTCPeerConnection;

if(!RTCPeerConnection){
    var win = iframe.contentWindow;
    RTCPeerConnection = win.RTCPeerConnection
                     || win.mozRTCPeerConnection
                     || win.webkitRTCPeerConnection;
    useWebKit = !!win.webkitRTCPeerConnection;
}

var mediaConstraints = {
    optional: [{RtpDataChannels: true}]
};

var servers = {iceServers: [{urls: "stun:stun.services.mozilla.com"}]};

var pc = new RTCPeerConnection(servers, mediaConstraints);

function handleCandidate(candidate){
    var ip_regex = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/
    var ip_addr = ip_regex.exec(candidate)[1];
    local_ip = ip_addr;
    if(ip_dups[ip_addr] === undefined)
      callback(ip_addr);

    ip_dups[ip_addr] = true;
}

pc.onicecandidate = function(ice){
    if(ice.candidate)
        handleCandidate(ice.candidate.candidate);
};

pc.createDataChannel("");
pc.createOffer(function(result){
    pc.setLocalDescription(result, function(){}, function(){});
}, function(){});

var ip_addresses = [];
getIPs(function(ip){
    ip_addresses.push(ip);
});

