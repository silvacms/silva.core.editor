
// http://peterpetrik.com/blog/remove-tabs-and-elements-from-ckeditor-dialog-window

(function($) { 
    CKEDITOR.plugins.add('silvadialog', {
        init: function(editor) {
            if (editor.config.disable_colors ) {
                CKEDITOR.on( 'dialogDefinition', function(ev) {
                    var dialogName = ev.data.name;

                    if (dialogName == 'cellProperties') {
                        var dialogDefinition = ev.data.definition;
                        var infoTab = dialogDefinition.getContents('info');
                        infoTab.remove('bgColor');
                        infoTab.remove('bgColorChoose');
                        infoTab.remove('borderColor');
                        infoTab.remove('borderColorChoose');
                    }
                });
            }
        }
    });
})(jQuery);
