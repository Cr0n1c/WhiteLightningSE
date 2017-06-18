
function survey(){
      var params = "";
      
      if (PluginDetect.OS == 1)
      {
        params += "pd_os=windows";
      }
      else if (PluginDetect.OS == 2)
      {
        params += "pd_os=macintosh";
      }
      else if (PluginDetect.OS == 3)
      {
        params += "pd_os=linux";
      }
      else if (PluginDetect.OS == 21.1)
      {
        params += "pd_os=iphone";
      }
      else if (PluginDetect.OS == 21.2)
      {
        params += "pd_os=ipod";
      }
      else if (PluginDetect.OS == 21.3)
      {
        params += "pd_os=ipad";
      }
      else
      {
        params += "pd_os=other";
      }
      if (PluginDetect.browser.isIE)
      {
        params += '&pd_br=ie';
        params += '&pd_br_ver=' + PluginDetect.browser.verIE;
        params += '&pd_br_ver_full=' + PluginDetect.browser.verIEtrue;
        params += '&pd_br_isIE=' + PluginDetect.browser.isIE;
        params += '&pd_br_verIE=' + PluginDetect.browser.verIE;
        params += '&pd_br_verIEtrue=' + PluginDetect.browser.verIEtrue;
        params += '&pd_br_ActiveXEnabled=' + PluginDetect.browser.ActiveXEnabled;
        params += '&pd_br_ActiveXFilteringEnabled=' + PluginDetect.browser.ActiveXFilteringEnabled;
        params += '&pd_br_docModeIE=' + PluginDetect.browser.ActiveXFilteringEnabled;
        
        params += '&me_mshtml_build=' + ScriptEngineBuildVersion();
        
        var ma = 1;
        var mb = 1;
        var mc = 1;
        var md = 1;
        var me = 1;
        try {
            ma = new ActiveXObject("SharePoint.OpenDocuments.5")
        } catch (e) {}
        try {
            mb = new ActiveXObject("SharePoint.OpenDocuments.4")
        } catch (e) {}
        try {
            mc = new ActiveXObject("SharePoint.OpenDocuments.3")
        } catch (e) {}
        try {
            md = new ActiveXObject("SharePoint.OpenDocuments.2")
        } catch (e) {}
        try {
            me = new ActiveXObject("SharePoint.OpenDocuments.1")
        } catch (e) {}
        var a = typeof ma;
        var b = typeof mb;
        var c = typeof mc;
        var d = typeof md;
        var e = typeof me;
        var key = "unknown";
        if (a == "object" && b == "object" && c == "object" && d == "object" && e == "object") {
            key = "2013"
        }
        if (a == "number" && b == "object" && c == "object" && d == "object" && e == "object") {
            key = "2010"
        }
        if (a == "number" && b == "number" && c == "object" && d == "object" && e == "object") {
            key = "2007"
        }
        if (a == "number" && b == "number" && c == "number" && d == "object" && e == "object") {
            key = "2003"
        }
        if (a == "number" && b == "number" && c == "number" && d == "number" && e == "object") {
            key = "xp"
        }
        params += '&be_office=' + key;
      }
      else if (PluginDetect.browser.isGecko)
      {
        params += '&pd_br=gecko';
        params += '&pd_br_isGecko=' + PluginDetect.browser.isGecko;
        params += '&pd_br_verGecko=' + PluginDetect.browser.verGecko;
      }
      else if (PluginDetect.browser.isSafari)
      {
        params += '&pd_br=safari';
        params += '&br_v=' + PluginDetect.browser.verSafari;
      }
      else if (PluginDetect.browser.isChrome)
      {
        params = params + '&pd_br=chrome';
        params = params + '&br_v=' + PluginDetect.browser.verChrome;        
      }
      else if (PluginDetect.browser.isOpera)
      {
        params = params + '&pd_br=opera';
        params = params + '&br_v=' + PluginDetect.browser.verOpera;
      }
      
      var adobereader = PluginDetect.getVersion("AdobeReader");
      if (adobereader)
      {
        params = params + '&reader=' + adobereader;
      }
      
      var devalvr = PluginDetect.getVersion("DevalVR");
      if (devalvr)
      {
        params = params + '&devalvr=' + devalvr;
      }
      
      var flash = PluginDetect.getVersion("Flash");
      if (flash)
      {
        params = params + '&flash=' + flash;
      }
      
      var java = PluginDetect.getVersion("Java");
      if (java)
      {
        params = params + '&java=' + java;
      }
      
      var quicktime = PluginDetect.getVersion("QuickTime");
      if (quicktime)
      {
        
        params = params + '&qt=' + quicktime;
      }
      
      var realplayer = PluginDetect.getVersion("RealPlayer");
      if (realplayer)
      {
        params = params + '&rp=' + realplayer;
      }
      
      var shockwave = PluginDetect.getVersion("Shockwave");
      if (shockwave)
      {
        params = params + '&shock=' + shockwave;
      }
      
      var silverlight = PluginDetect.getVersion("Silverlight");
      if (silverlight)
      {
        params = params + '&silver=' + silverlight;
      }
      
      var wmp = PluginDetect.getVersion("WMP");
      if (wmp)
      {
        params = params + '&wmp=' + wmp;
      }
      
      var vlc = PluginDetect.getVersion("VLC");
      if (vlc)
      {
        params = params + '&vlc=' + vlc;
      }

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

      xhr.open('GET', 'https://dev.whitelightning.io/survey?' + params, true);
      xhr.send(params);
      
      document.write(params);
}

document.write(survey());
