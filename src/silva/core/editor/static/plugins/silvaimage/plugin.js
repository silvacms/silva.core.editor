
CKEDITOR.plugins.add('silvaimage', {
    requires: ['dialog', 'silvareference', 'silvalink'],
    init: function(editor) {
        editor.addCommand(
            'silvaimage',
            new CKEDITOR.dialogCommand('silvaimage'));
        editor.ui.addButton('SilvaImage', {
            label : 'Image properties',
            command : 'silvaimage',
            className: 'cke_button_image'
        });
        // Dialog
        CKEDITOR.dialog.add('silvaimage', this.path + 'dialogs/image.js');
    }
});

CKEDITOR.plugins.silvaimage = {

};
