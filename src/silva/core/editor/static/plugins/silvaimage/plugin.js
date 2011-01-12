
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
            var base = null;

            if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                base = selection.getSelectedElement();
            } else {
                base = selection.getStartElement();
            };

            var element = base.getAscendant('div', true);

            if (CKEDITOR.plugins.silvaimage.isImage(element)) {
                return element;
            };
            return null;
        }
        catch(e) {
            return null;
        }
    }
};

(function(){
    var API = CKEDITOR.plugins.silvaimage;

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
                var element = API.getSelectedImage(editor);
                var imageCommand = editor.getCommand('silvaimage');

                if (element != null) {
                    imageCommand.setState(CKEDITOR.TRISTATE_ON);
                } else {
                    imageCommand.setState(CKEDITOR.TRISTATE_OFF);
                };
            });
            editor.on('doubleclick', function(event){
                var element = API.getSelectedImage(editor);

                if (element != null) {
                    event.data.dialog = 'silvaimage';
                };
            });
            // Dialog
            CKEDITOR.dialog.add('silvaimage', this.path + 'dialogs/image.js');
            // Menu
            if (editor.addMenuItems) {
                editor.addMenuItems({
                    image: {
                        label: editor.lang.image.menu,
                        command : 'silvaimage',
                        group : 'image',
                        order: 1
                    }
                });
            };
            if (editor.contextMenu) {
                editor.contextMenu.addListener(function(element, selection) {
                    if (API.isImage(element.getAscendant('div', true))) {
                        return  {
                            image: CKEDITOR.TRISTATE_OFF
                        };
                    };
                    return null;
                });
            };
        }
    });
})();
