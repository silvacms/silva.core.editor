
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
        editor.addCss(
            'div.image' +
                '{' +
                'padding: 1px;' +
                'color: #444;' +
                'background-color: #EEE8AA;' +
                'display: inline-block' +
                '}');
        editor.addCss(
            'div.image span.caption {' +
                'display: block;' +
                'padding-left: 5px' +
                '}');
        editor.addCss(
            'div.float-left {' +
                'float: left;' +
                '}');
        editor.addCss(
            'div.float-right {' +
                'float: right;' +
                '}');
        editor.addCss(
            'div.image-left {' +
                'text-align: left;' +
                '}');
        editor.addCss(
            'div.image-right {' +
                'text-align: right;' +
                '}');
        editor.addCss(
            'div.image-center {' +
                'text-align: center;' +
                '}');
        // Events
        editor.on('selectionChange', function(event) {
            var element = CKEDITOR.plugins.silvaimage.getSelectedImage(editor);
            var imageCommand = editor.getCommand('silvaimage');

            if (element != null) {
                imageCommand.setState(CKEDITOR.TRISTATE_ON);
            } else {
                imageCommand.setState(CKEDITOR.TRISTATE_OFF);
            };
        });
        editor.on('doubleclick', function(event){
            var element = CKEDITOR.plugins.silvaimage.getSelectedImage(editor);

            if (element != null) {
                event.data.dialog = 'silvaimage';
            };
        });
        // Dialog
        CKEDITOR.dialog.add('silvaimage', this.path + 'dialogs/image.js');
    }
});

CKEDITOR.plugins.silvaimage = {
    isImage: function(element) {
        if (element != null && element.is('div') && element.hasClass('image')) {
            return true;
        };
        return false;
    },
    getSelectedImage: function(editor) {
        try {
            var selection = editor.getSelection();
            if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                var selectedElement = selection.getSelectedElement().getAscendant('div', true);
                if (CKEDITOR.plugins.silvaimage.isImage(selectedElement)) {
                    return selectedElement;
                };
            };

            var ranges = selection.getRanges(true)[0];
            ranges.shrink(CKEDITOR.SHRINK_TEXT);

            var base = ranges.getCommonAncestor();
            var selectedElement = base.getAscendant('div', true);
            if (CKEDITOR.plugins.silvaimage.isImage(selectedElement)) {
                return selectedElement;
            };
            return null;
        }
        catch(e) {
            return null;
        }
    }
};
