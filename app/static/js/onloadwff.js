$(function () {
    $.getJSON(
        "chrome-extension://hdokiejnpimakedhajhdlcegeplioahd/manifest.json",
        function (data) {
            $("#reply").html(JSON.stringify(data));
            // or work with the data here, already in object format
                     });
                     });
            

