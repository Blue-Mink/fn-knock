try {
        var qp = new URLSearchParams(location.search);
        var modeApps = qp.get('apps') === '1';
        var modePortal = qp.get('portal') === '1';
        if (!modeApps && !modePortal) return;
        var FT = modePortal ? '敲门门户' : '敲门应用';
        try {
          Object.defineProperty(document, 'title', {
            configurable: true,
            get: function () { return FT; },
            set: function () {}
          });
        } catch (e) {}
        var fixTitle = function () {
          var t = document.querySelector('title');
          if (t && t.textContent !== FT) t.textContent = FT;
        };
        fixTitle();
        new MutationObserver(fixTitle).observe(document.documentElement, { childList: true, subtree: true, characterData: true });
        if (modePortal) {
          var hide = document.createElement('style');
          hide.textContent = '#app{display:none!important}html,body{background:#0b0b0d;height:100%}';
          document.head.appendChild(hide);
          var fr = document.createElement('iframe');
          fr.src = location.protocol + '//' + location.hostname + ':7999/__select__';
          fr.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;border:0';
          document.documentElement.appendChild(fr);
          var ivp = setInterval(function () { fixTitle(); if (!document.contains(fr)) document.documentElement.appendChild(fr); }, 500);
          return;
        }
        var st = document.createElement('style');
        st.textContent = __APPS_CSS__;
        document.head.appendChild(st);
        var opened = false;
        var openApps = function () {
          var b = Array.from(document.querySelectorAll('button[aria-haspopup="dialog"]'))
            .find(function (x) { return /应用|applicat/i.test(x.getAttribute('aria-label') || ''); });
          if (b) { b.click(); return true; }
          return false;
        };
        var iv = setInterval(function () {
          if (openApps()) { clearInterval(iv); opened = true; }
        }, 100);
        setTimeout(function () { clearInterval(iv); }, 10000);
        new MutationObserver(function () {
          if (opened && !document.querySelector('[role="dialog"]')) {
            setTimeout(function () {
              if (!document.querySelector('[role="dialog"]')) openApps();
            }, 100);
          }
        }).observe(document.body, { childList: true });
      } catch (e) {}
