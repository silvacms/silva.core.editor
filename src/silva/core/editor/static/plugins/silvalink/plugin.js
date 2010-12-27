
(function($) {
    CKEDITOR.plugins.add('silvalink', {
        requires: ['dialog'],
        init: function(editor) {
            editor.addCommand(
                'silvalink',
                new CKEDITOR.dialogCommand('silvalink'));
            editor.ui.addButton('SilvaLink', {
                label : 'Link a content',
                command : 'silvalink',
                className: 'cke_button_link'
            });

            // XXX template URL.
            var templateURL = $('head base').attr('href').replace(
                    /\/edit$/,
                '/++resource++Products.SilvaDocument.smi/test.jst');
            var createReferenceUI = function(referenceTemplate) {
                // Create the reference UI element with the given
                // template.
                CKEDITOR.tools.extend(CKEDITOR.ui.dialog, {
                    reference: function(dialog, elementDefinition, htmlList) {
                        if (!arguments.length)
                            return;
                        var identifier = elementDefinition.id;
                        this._ = {};
                        this._.id = identifier;
                        this._.remote = new ReferencedRemoteObject(identifier);
                        var innerHTML = function() {
                            return referenceTemplate.expand({id: identifier});
                        };
                        CKEDITOR.ui.dialog.labeledElement.call(
                            this, dialog, elementDefinition, htmlList, innerHTML);
                    }
                }, true);
                CKEDITOR.ui.dialog.reference.prototype = CKEDITOR.tools.extend(
                    new CKEDITOR.ui.dialog.labeledElement, {
                        getInputElement: function() {
                            return CKEDITOR.document.getById(this._.remote.get_reference_input().id);
                        },
                        getValue: function() {
                            return this._.remote.reference();
                        },
                        setValue: function(value) {
                            this._.remote.fetch(value);
                        },
                        clear: function() {
                            this._.remote.clear();
                        }
                    }, true);
                CKEDITOR.dialog.addUIElement('reference', {
                    build: function(dialog, elementDefinition, output) {
                        return new CKEDITOR.ui.dialog[elementDefinition.type](
                            dialog, elementDefinition, output);
                    }
                });
            };

            // Fetch reference UI template from the server and create
            // the UI element.
            $.ajax({
                url: templateURL,
                dataType: 'html',
                success: function(template) {
                    createReferenceUI(new jsontemplate.Template(template, {}));
                }
            });

            CKEDITOR.dialog.add('silvalink', this.path + 'dialogs/link.js');
        }
    });
})(jQuery);

CKEDITOR.plugins.silvalink = {
    getSelectedLink: function(editor) {
        try {
            var selection = editor.getSelection();
            if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                var selectedElement = selection.getSelectedElement();
                if (selectedElement.is('a'))
                    return selectedElement;
            }

            var range = selection.getRanges(true)[ 0 ];
            range.shrink(CKEDITOR.SHRINK_TEXT);
            var root = range.getCommonAncestor();
            return root.getAscendant('a', true);
        }
        catch(e) {
            return null;
        }
    }
};
