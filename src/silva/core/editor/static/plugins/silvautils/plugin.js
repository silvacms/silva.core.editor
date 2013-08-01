(function($, jsontemplate, CKEDITOR) {
    if (CKEDITOR.env.ie) {
        CKEDITOR.plugins.silvautils = {
            getSelectedElement: function(editor) {
                var selection = selection = editor.document.$.selection,
                    range;

                if (selection.type != "None") {
                    range = editor.document.$.selection.createRange();
                    if (selection.type == "Text") {
                        return new CKEDITOR.dom.element(range.parentElement);
                    };
                    if (range.length > 0) {
                        return new CKEDITOR.dom.element(range.item(0));
                    };
                };
                return null;
            },
            /**
             * Given a block element with contenteditable set to false,
             * select it in the editor.
             */
            selectBlock: function(editor, block) {
                var selection = editor.getSelection(),
                    range;

                if (selection === null)  {
                    return;
                };
                selection.unlock();
                range = editor.document.$.body.createControlRange();
                range.add(block.$);
                range.select();
                // Force CKEditor to refresh it caches. We need to 'lock'
                // our changes to prevent them to be reverted by CKEditor.
                selection.lock();
                editor.forceNextSelectionCheck();
                editor.selectionChange(true);
                setTimeout(function() {
                    // The modification should have been done, 'unlock' to
                    // restore the editor features.
                    selection.unlock();
                }, 100);
            },
            /**
             * Given a text node, move the caret at the begining or the
             * end of it.
             */
            selectText: function(editor, text, at_the_end) {
                var selection = editor.getSelection(),
                    range;

                if (selection === null)  {
                    return;
                };
                selection.unlock();
                // CKEditor utilities doesn't seems to work on IE. Do
                // it manually.
                range = editor.document.$.body.createTextRange();
                range.moveToElementText(text.$);
                range.collapse(!at_the_end);
                range.scrollIntoView();
                range.select();
                // Force CKEditor to refresh it caches. We need to 'lock'
                // our changes to prevent them to be reverted by CKEditor.
                selection.lock();
                editor.forceNextSelectionCheck();
                editor.selectionChange(true);
                setTimeout(function() {
                    // The modification should have been done, 'unlock' to
                    // restore the editor features.
                    selection.unlock();
                }, 100);
            }
        };
    } else {
        CKEDITOR.plugins.silvautils = {
            getSelectedElement: function(editor) {
                var selection = editor.document.$.getSelection(),
                    range;

                if (selection.rangeCount > 0) {
                    range = selection.getRangeAt(0);
                    if (range.commonAncestorContainer !== null) {
                        return new CKEDITOR.dom.element(range.commonAncestorContainer);
                    }
                };
                return null;
            },
            /**
             * Given a block element with contenteditable set to false,
             * select it in the editor.
             */
            selectBlock: function(editor, block) {
                var selection, range;

                if (editor.getSelection() === null)  {
                    return;
                };
                range = editor.document.$.createRange();
                if (CKEDITOR.env.webkit) {
                    range.selectNodeContents(block.$);
                } else {
                    range.selectNode(block.$);
                };
                selection = editor.document.$.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                editor.document.fire('selectionchange');
            },
            /**
             * Given a text node, move the caret at the begining or the
             * end of it.
             */
            selectText: function(editor, text, at_the_end) {
                var selection, range;

                if (editor.getSelection() === null)  {
                    return;
                };
                range = editor.document.$.createRange();
                range.selectNodeContents(text.$);
                range.collapse(!at_the_end);
                text.scrollIntoView();
                selection = editor.document.$.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                editor.document.fire('selectionchange');
            }
        };
    };

    CKEDITOR.plugins.add('silvautils', {
        init: function(editor) {
            /**
             * Support for the reference widget inside CKEditor.
             */
            var templateURL = $('#content-url').attr('href') + '/++rest++silva.core.editor.widget.reference';

            var createReferenceUI = function(referenceTemplate) {
                // Create the reference UI element with the given
                // template.
                CKEDITOR.tools.extend(CKEDITOR.ui.dialog, {
                    reference: function(dialog, elementDefinition, htmlList) {
                        var identifier = dialog.getName() + '-' + elementDefinition.id;
                        var self = this;

                        this._ = {};

                        dialog.on('load', function() {
                            self._.remote = ReferencedRemoteObject($('#' + identifier));
                            self._.remote.change(function(event, info) {
                                self.fire('reference-update', info);
                            });
                            $('#' + self.domId).SMIReferenceLookup();
                        });

                        var innerHTML = function() {
                            var data = {};

                            data.id = identifier;
                            if (elementDefinition.content != undefined) {
                                data.content = elementDefinition.content;
                            }
                            return referenceTemplate.expand(data);
                        };
                        CKEDITOR.ui.dialog.labeledElement.call(
                            this, dialog, elementDefinition, htmlList, innerHTML);
                    }
                }, true);
                CKEDITOR.ui.dialog.reference.prototype = CKEDITOR.tools.extend(
                    new CKEDITOR.ui.dialog.labeledElement, {
                        getInputElement: function() {
                            return CKEDITOR.document.getById(this._.remote.identifier);
                        },
                        getValue: function() {
                            return this._.remote.reference();
                        },
                        setValue: function(value) {
                            this._.remote.fetch(value);
                        },
                        clear: function() {
                            this._.remote.clear();
                        },
                        eventProcessors: CKEDITOR.tools.extend({}, CKEDITOR.ui.dialog.uiElement.prototype.eventProcessors, {
                            onReferenceUpdate: function(dialog, func) {
                                this.on('reference-update', func);
                            }
                        }, true)
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
        }
    });
})(jQuery, jsontemplate, CKEDITOR);
