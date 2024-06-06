if (!window.dash_clientside) { window.dash_clientside = {}; }
window.dash_clientside.clientside = {
    redirect: function(path) {
        if (path) {
            window.location.href = window.location.origin + path;
        }
    }
};