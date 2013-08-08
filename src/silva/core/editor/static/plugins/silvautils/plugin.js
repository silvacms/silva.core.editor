(function($, jsontemplate, CKEDITOR) {
    /**
     * Silva module
     */
    CKEDITOR.silva = {};

    /**
     * Regular expression helper.
     */
    CKEDITOR.silva.RE = function(pattern, fallback, position) {
        this.pattern = pattern;
        this.fallback = fallback;
        this.position = position !== undefined ? position : 1;
    };
    CKEDITOR.silva.RE.prototype.extract = function(value) {
        var result = this.pattern.exec(value);

        if (result !== null) {
            return result[this.position];
        }
        return this.fallback;
    };

    /**
     * htmlParser helper for wrapper, used in the editor for
     * non-editable blocks (like images and external sources).
     */
    CKEDITOR.silva.parser = {};
    CKEDITOR.silva.parser.Wrapper = function(test, category) {
        this.test = test;
        this.category = category;
        if (category) {
            this.css = 'inline-container ' + category + ' ';
            this.pattern = new RegExp('^inline-container ' + category);
        } else {
            this.css = 'inline-container ';
            this.pattern = new RegExp('^inline-container');
        };
    };
    CKEDITOR.silva.parser.Wrapper.prototype = {
        /**
         * Return true if the element is a wrapper.
         */
        is: function(element) {
            return (element &&
                    element.name == 'span' &&
                    element.attributes['class'] != null &&
                    element.attributes['class'].match(this.pattern));
        },
        /**
         * Wrap the element inside a wrapper.
         */
        wrap: function(element, alignement) {
            var parent = element.parent,
                container;

            if (!this.is(parent)) {
                container = new CKEDITOR.htmlParser.element(
                    'span', {'class': this.css + alignement});
                if (CKEDITOR.env.webkit) {
                    // To help the selection in
                    // Chrome we add a space before
                    // and after each source.
                    container.children = [
                        new CKEDITOR.htmlParser.text(''),
                        element,
                        new CKEDITOR.htmlParser.text('')];
                } else {
                    container.children = [element];
                };
                if (!CKEDITOR.env.gecko) {
                    container.attributes['contenteditable'] = 'false';
                };
                container.parent = parent;
                element.parent = container;
                return container;
            };
            return null;
        },
        /**
         * Remove an existing wrapper.
         */
        remove: function(element) {
            var i, len, children = [];

            if (this.is(element)) {
                for (i=0, len=element.children.length; i < len; i++) {
                    if (this.test(element.children[i])) {
                        children.push(element.children[i]);
                        break;
                    };
                };
                return children[0];
            };
            return null;
        }
    };

    /**
     * Utilities functions.
     */
    if (CKEDITOR.env.ie) {
        CKEDITOR.silva.utils = {
            /**
             * Return a element where the current selection points to
             * (IE implementation).
             */
            getSelectedElement: function(editor) {
                var selection = selection = editor.document.$.selection,
                    range = selection.createRange(),
                    element = null;

                if (selection.type == "Control") {
                    element = range.item(0);
                } else {
                    element = range.parentElement();
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
        CKEDITOR.silva.utils = {
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
    CKEDITOR.silva.utils = CKEDITOR.tools.extend(CKEDITOR.silva.utils, {
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
            (function() {
                // Patch dtd. Span are like div now, because of the support for inline-container.
                for (var key in CKEDITOR.dtd) {
                    if (!!CKEDITOR.dtd[key]['span']) {
                        delete CKEDITOR.dtd[key]['span'];
                    };
                    if (!!CKEDITOR.dtd[key]['div']) {
                        CKEDITOR.dtd[key]['span']  = 1;
                    };
                    CKEDITOR.dtd['span']['div'] = 1;
                    CKEDITOR.dtd['span']['a'] = 1; // For image link (the caption).
                }
            })();

            /**
             * Support for inline-container helper, used for
             * non-editable block in CKEditor.
             */
            editor.addCss(
                'span.inline-container {' +
                    'display: inline-block;' +
                    '}');
            editor.addCss(
                'span.inline-container.float-left {' +
                    'float: left;' +
                    '}');
            editor.addCss(
                'span.inline-container.float-right {' +
                    'float: right;' +
                    '}');
            editor.addCss(
                'span.inline-container.align-left {' +
                    'text-align: left;' +
                    'display: block;' +
                    '}');
            editor.addCss(
                'span.inline-container.align-right {' +
                    'text-align: right;' +
                    'display: block;' +
                    '}');
            editor.addCss(
                'span.inline-container.align-center {' +
                    'text-align: center;' +
                    'display: block;' +
                    '}');

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
