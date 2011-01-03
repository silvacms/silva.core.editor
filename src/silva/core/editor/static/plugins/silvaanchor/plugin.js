
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
            var element = CKEDITOR.plugins.silvaanchor.getSelectedAnchor(editor);
            var anchorCommand = editor.getCommand('silvaanchor');

            if (element != null) {
                anchorCommand.setState(CKEDITOR.TRISTATE_ON);
            } else {
                anchorCommand.setState(CKEDITOR.TRISTATE_OFF);
            };
        });
        editor.on('doubleclick', function(event) {
            var element = CKEDITOR.plugins.silvaanchor.getSelectedAnchor(editor);

            if (element != null) {
                event.data.dialog = 'silvaanchor';
            };
        });
        // Dialog
        CKEDITOR.dialog.add('silvaanchor', this.path + 'dialogs/anchor.js');
    }
});

CKEDITOR.plugins.silvaanchor = {
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
                anchors.push([candidate.getAttribute('name'),
                              candidate.getAttribute('title')]);
            };
        };
        return anchors;
    }
};
