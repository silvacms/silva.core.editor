

(function(CKEDITOR) {

    CKEDITOR.plugins.silvaanchor = {
        getAnchorTextFromAttributes: function(attributes) {
            var text = '[#' + attributes['name'];
            if (attributes['title']) {
                text += ': ' + attributes['title'];
            };
            text += ']';
            return text;
        },
        isAnchor: function(element) {
            if (element != null && element.is('a') && element.hasClass('anchor')) {
                return true;
            };
            return false;
        },
        getSelectedAnchor: function(editor) {
            try {
                var selection = editor.getSelection();

                if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                    var selectedElement = selection.getSelectedElement();
                    if (CKEDITOR.plugins.silvaanchor.isAnchor(selectedElement)) {
                        return selectedElement;
                    };
                };

                var ranges = selection.getRanges(true)[0];
                if (ranges != undefined) {
                    ranges.shrink(CKEDITOR.SHRINK_TEXT);

                    var base = ranges.getCommonAncestor();
                    var selectedElement = base.getAscendant('a', true);
                    if (CKEDITOR.plugins.silvaanchor.isAnchor(selectedElement)) {
                        return selectedElement;
                    };
                };
                return null;
            } catch(e) {
                return null;
            }
        },
        listDocumentAnchors: function(editor) {
            var anchors = [];
            var candidates = new CKEDITOR.dom.nodeList(editor.document.$.anchors);

            for (var i=0; i < candidates.count(); i++) {
                var candidate = candidates.getItem(i);

                if (CKEDITOR.plugins.silvaanchor.isAnchor(candidate)) {
                    var name = candidate.getAttribute('name');
                    var title = name;

                    if (candidate.hasAttribute('title')) {
                        title = candidate.getAttribute('title');
                    };
                    anchors.push([name, title]);
                };
            };
            return anchors;
        }
    };

    var API = CKEDITOR.plugins.silvaanchor;

    CKEDITOR.removeSilvaAnchorCommand = function() {};
    CKEDITOR.removeSilvaAnchorCommand.prototype = {
        exec: function(editor) {
            var anchor = API.getSelectedAnchor(editor);
            if (anchor !== null) {
                anchor.remove();
            }
        },
        startDisabled: true
    };

    CKEDITOR.plugins.add('silvaanchor', {
        requires: ['dialog', 'htmldataprocessor'],
        init: function(editor) {
            editor.addCommand(
                'silvaanchor',
                new CKEDITOR.dialogCommand('silvaanchor'));
            editor.addCommand(
                'silvaremoveanchor',
                new CKEDITOR.removeSilvaAnchorCommand());
            editor.ui.addButton('SilvaAnchor', {
                label : 'Anchor properties',
                command : 'silvaanchor',
                className: 'cke_button_anchor'
            });
            editor.ui.addButton('SilvaRemoveAnchor', {
                label : 'Remove anchor',
                command : 'silvaremoveanchor',
                className: 'cke_button_removeanchor'
            });
            editor.addCss(
                'a.anchor' +
                    '{' +
                    'padding: 1px;' +
                    'color: #444;' +
                    'background-color: #ffb;' +
                    '}'
            );
            // Events
            editor.on('selectionChange', function(event) {
                var anchor = API.getSelectedAnchor(editor);
                var command_edit = editor.getCommand('silvaanchor');
                var command_remove = editor.getCommand('silvaremoveanchor');

                if (anchor != null) {
                    command_edit.setState(CKEDITOR.TRISTATE_ON);
                    command_remove.setState(CKEDITOR.TRISTATE_ON);
                } else {
                    command_edit.setState(CKEDITOR.TRISTATE_OFF);
                    command_remove.setState(CKEDITOR.TRISTATE_OFF);
                };
            });
            editor.on('doubleclick', function(event) {
                var anchor = API.getSelectedAnchor(editor);

                if (anchor != null) {
                    event.data.dialog = 'silvaanchor';
                };
            });
            // Dialog
            CKEDITOR.dialog.add('silvaanchor', this.path + 'dialogs/anchor.js');
            // Menu
            if (editor.addMenuItems) {
                editor.addMenuItems({
                    silvaanchor: {
                        label: editor.lang.anchor.menu,
                        command : 'silvaanchor',
                        group : 'link',
                        className: 'cke_button_anchor',
                        order: 5
                    },
                    silvaremoveanchor: {
                        label: 'Remove anchor',
                        command : 'silvaremoveanchor',
                        className: 'cke_button_removeanchor',
                        group : 'link',
                        order: 6
                    }
                });
            };
            if (editor.contextMenu) {
                editor.contextMenu.addListener(function(element, selection) {
                    if (API.isAnchor(element)) {
                        return  {
                            silvaanchor: CKEDITOR.TRISTATE_OFF,
                            silvaremoveanchor: CKEDITOR.TRISTATE_OFF
                        };
                    };
                    return null;
                });
            };
        },
        afterInit: function(editor) {
            // Input / Output transformations
            var dataProcessor = editor.dataProcessor;
            var dataFilter = dataProcessor && dataProcessor.dataFilter;
            var htmlFilter = dataProcessor && dataProcessor.htmlFilter;

            if (dataFilter) {
                dataFilter.addRules({
                    elements: {
                        a: function(element) {
                            var attributes = element.attributes;

                            if (attributes['class'] == 'anchor') {
                                if (!element.children.length) {
                                    var text = API.getAnchorTextFromAttributes(attributes);
                                    element.children.push(
                                        new CKEDITOR.htmlParser.fragment.fromHtml(text)
                                    );
                                };
                                attributes['contenteditable'] = 'false';
                            };
                            return null;
                        }
                    }
                });
            };
            if (htmlFilter) {
                htmlFilter.addRules({
                    elements: {
                        a: function(element) {
                            var attributes = element.attributes;
                            if (attributes['class'] == 'anchor') {
                                if (element.children.length) {
                                    element.children = [];
                                };

                                var clean = function(name) {
                                    if (attributes[name]) {
                                        delete attributes[name];
                                    };
                                };

                                clean('_cke_saved_href');
                                clean('contenteditable');
                                clean('href');
                            };
                            return null;
                        }
                    }
                });
            };
        }
    });
})(CKEDITOR);
