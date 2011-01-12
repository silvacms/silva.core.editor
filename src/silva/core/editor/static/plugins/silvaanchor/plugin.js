
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
            ranges.shrink(CKEDITOR.SHRINK_TEXT);

            var base = ranges.getCommonAncestor();
            var selectedElement = base.getAscendant('a', true);
            if (CKEDITOR.plugins.silvaanchor.isAnchor(selectedElement)) {
                return selectedElement;
            };
            return null;
        }
        catch(e) {
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

(function() {
    var API = CKEDITOR.plugins.silvaanchor;

    CKEDITOR.plugins.add('silvaanchor', {
        requires: ['dialog', 'htmldataprocessor'],
        init: function(editor) {
            editor.addCommand(
                'silvaanchor',
                new CKEDITOR.dialogCommand('silvaanchor'));
            editor.ui.addButton('SilvaAnchor', {
                label : 'Anchor properties',
                command : 'silvaanchor',
                className: 'cke_button_anchor'
            });
            editor.addCss(
                'a.anchor' +
                    '{' +
                    'padding: 1px;' +
                    'color: #444;' +
                    'background-color: #EEE8AA;' +
                    '}'
            );
            // Events
            editor.on('selectionChange', function(event) {
                var element = API.getSelectedAnchor(editor);
                var anchorCommand = editor.getCommand('silvaanchor');

                if (element != null) {
                    anchorCommand.setState(CKEDITOR.TRISTATE_ON);
                } else {
                    anchorCommand.setState(CKEDITOR.TRISTATE_OFF);
                };
            });
            editor.on('doubleclick', function(event) {
                var element = API.getSelectedAnchor(editor);

                if (element != null) {
                    event.data.dialog = 'silvaanchor';
                };
            });
            // Dialog
            CKEDITOR.dialog.add('silvaanchor', this.path + 'dialogs/anchor.js');
            // Menu
            if (editor.addMenuItems) {
                editor.addMenuItems({
                    anchor: {
                        label: editor.lang.anchor.menu,
                        command : 'silvaanchor',
                        group : 'link',
                        order: 5
                    }
                });
            };
            if (editor.contextMenu) {
                editor.contextMenu.addListener(function(element, selection) {
                    if (API.isAnchor(element)) {
                        return  {
                            anchor: CKEDITOR.TRISTATE_OFF
                        };
                    };
                    return null;
                });
            };
        },
        afterInit: function(editor) {
            // Register a filter to fill in anchor data.

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
})();
