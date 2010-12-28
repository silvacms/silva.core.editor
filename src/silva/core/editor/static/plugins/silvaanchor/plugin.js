
CKEDITOR.plugins.add('silvaanchor', {
    requires: ['dialog'],
    init: function(editor) {
        editor.addCommand(
            'silvaanchor',
            new CKEDITOR.dialogCommand('silvaanchor'));
        editor.ui.addButton('SilvaAnchor', {
            label : 'Anchor properties',
            command : 'silvaanchor',
            className: 'cke_button_anchor'
            });
        CKEDITOR.dialog.add('silvaanchor', this.path + 'dialogs/anchor.js');
    }
});
