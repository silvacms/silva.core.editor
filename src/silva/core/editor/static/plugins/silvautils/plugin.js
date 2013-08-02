(function($, jsontemplate, CKEDITOR) {
    if (CKEDITOR.env.ie) {
        CKEDITOR.plugins.silvautils = {
            /**
             * Return a element where the current selection points to
             * (IE implementation).
             */
            getSelectedElement: function(editor) {
                var selection = selection = editor.document.$.selection,
                    range,
                    element = null;

                if (selection.type != "None") {
                    range = editor.document.$.selection.createRange();
                    if (selection.type == "Text") {
                        element = range.parentElement();
                    } else if (range.length > 0) {
                        element = range.item(0);
                    };
                };
                if (element !== null) {
                    return new CKEDITOR.dom.element(element);
                };
                return null;
            },
            /**
             * Given a block element with contenteditable set to false,
             * select it in the editor (IE implementation).
             */
            selectBlock: function(editor, block) {
                var selection = editor.getSelection(),
                    range;

                if (selection !== null)  {
                    selection.unlock();
                };
                range = editor.document.$.body.createControlRange();
                range.add(block.$);
                range.select();
                // Force CKEditor to refresh it caches. We need to 'lock'
                // our changes to prevent them to be reverted by CKEditor.
                if (selection === null) {
                    selection = editor.getSelection();
                };
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
             * end of it (IE implementation).
             */
            selectText: function(editor, text, at_the_end) {
                var selection = editor.getSelection(),
                    range;

                if (selection !== null)  {
                    selection.unlock();
                };
                // CKEditor utilities doesn't seems to work on IE. Do
                // it manually.
                range = editor.document.$.body.createTextRange();
                range.moveToElementText(text.$);
                range.collapse(!at_the_end);
                range.scrollIntoView();
                range.select();
                // Force CKEditor to refresh it caches. We need to 'lock'
                // our changes to prevent them to be reverted by CKEditor.
                if (selection === null) {
                    selection = editor.getSelection();
                };
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
            /**
             * Return a element where the current selection points to
             * (non-IE implementation).
             */
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
             * select it in the editor (non-IE implementation).
             */
            selectBlock: function(editor, block) {
                var selection, range;

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
             * end of it (non-IE implementation).
             */
            selectText: function(editor, text, at_the_end) {
                var selection, range;

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
    CKEDITOR.plugins.silvautils = CKEDITOR.tools.extend(CKEDITOR.plugins.silvautils, {
        /**
         * Get (or add) a paragraph before (or after) the targeted
         * element.
         */
        getParagraph: function(editor, target, before_target) {
            var result;

            if (before_target) {
                result = target.getPrevious();
                if (result === null || result.getName() != 'p') {
                    result = editor.document.createElement('p');
                    CKEDITOR.env.webkit && result.appendBogus();
                    result.insertBefore(target);
                };
            } else {
                result = target.getNext();
                if (result === null || result.getName() != 'p') {
                    result = editor.document.createElement('p');
                    CKEDITOR.env.webkit && result.appendBogus();
                    result.insertAfter(target);
                };
            };
            return result;
        }
    });

    CKEDITOR.plugins.add('silvautils', {
        requires: ['selection'],
        init: function(editor) {
            // Patch selection to select the whole contenteditable
            // instead of only a element in it (this prevent to select an image in FF)
            (function () {
                if (CKEDITOR.dom.selection.prototype.origSelectElement === undefined) {
                    CKEDITOR.dom.selection.prototype.origSelectElement = CKEDITOR.dom.selection.prototype.selectElement;
                    CKEDITOR.dom.selection.prototype.selectElement = function(element) {
                        var div = element.getAscendant('div', true);

                        while (div !== null && div.getAttribute('contenteditable') !== 'false') {
                            div = div.getAscendant('div', false);
                        };
                        if (div !== null) {
                            element = div;
                        };
                        return this.origSelectElement(element);
                    };
                };
            })();

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
