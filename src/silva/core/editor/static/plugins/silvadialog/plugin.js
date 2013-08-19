
// http://peterpetrik.com/blog/remove-tabs-and-elements-from-ckeditor-dialog-window

(function($) {
    CKEDITOR.plugins.add('silvadialog', {
        init: function(editor) {
                CKEDITOR.on( 'dialogDefinition', function(ev) {
                    var dialogName = ev.data.name;
                    var dialogDefinition = ev.data.definition;
                    if (editor.config.disable_colors && dialogName == 'cellProperties') {
                        var infoTab = dialogDefinition.getContents('info');
                        infoTab.remove('bgColor');
                        infoTab.remove('bgColorChoose');
                        infoTab.remove('borderColor');
                        infoTab.remove('borderColorChoose');
                    }
                    if (dialogName == 'table' || dialogName == 'tableProperties') {
                        var advancedTab = dialogDefinition.getContents('advanced');
                        advancedTab.remove('advCSSClasses');
                        var infoTableTab = dialogDefinition.getContents('info');
                        infoTableTab.get('txtWidth')['default'] = '';
                        infoTableTab.remove('txtCellSpace');
                        infoTableTab.remove('txtCellPad');
                        infoTableTab.remove('txtBorder');
                        infoTableTab.remove('cmbAlign');
                    }
                });
        }
    });
})(jQuery);
