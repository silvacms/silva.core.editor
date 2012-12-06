CKEDITOR.skins.add('silva', (function () {
    var a = [];
    if (CKEDITOR.env.ie && CKEDITOR.env.version < 7) a.push('icons.png', 'images/sprites_ie6.png', 'images/dialog_sides.gif');
    return {
        preload: a,
        editor: {
            css: ['editor.css']
        },
        dialog: {
            css: ['dialog.css']
        },
        templates: {
            css: ['templates.css']
        },
        margins: [0, 14, 18, 14]
    };
})());
(function () {
    CKEDITOR.dialog ? a() : CKEDITOR.on('dialogPluginReady', a);

    function a() {
        CKEDITOR.dialog.on('resize', function (b) {
            var c = b.data,
                d = c.width,
                e = c.height,
                f = c.dialog,
                g = f.parts.contents;
            if (c.skin != 'silva') return;
            g.setStyles({
                width: d + 'px',
                height: e + 'px'
            });
            return;
        });
    };
})();
