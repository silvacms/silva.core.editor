

// createDialogFields is defined in plugin.js as it is used by other plugins

CKEDITOR.dialog.add('silvalink', function(editor) {

    return {
        title: 'Link properties',
        minWidth: 350,
        minHeight: 230,
        contents: [
            { id: 'link',
              elements: CKEDITOR.plugins.silvalink.createDialogFields()
            }
        ],
        onShow: function() {
            var data = {};
            var editor = this.getParentEditor();
            var element = CKEDITOR.plugins.silvalink.getSelectedLink(editor);

            data.link = {};
            if (element != null) {
                // Read and load link information
                var link = element.$;

                data.link.title = link.getAttribute('title');
                data.link.target = link.getAttribute('target');
                data.link.anchor = link.getAttribute('silva_anchor');
                if (link.hasAttribute('silva_reference')) {
                    data.link.type = 'intern';
                    data.link.content = link.getAttribute('silva_target');
                } else {
                    data.link.type = 'extern';
                    data.link.url = link.getAttribute('href');
                };
            } else {
                // Default values, there are no link here
                data.link.type = 'intern';
                data.link.target = '_self';
            };
            this.setupContent(data);
        },
        onOk: function() {
            var data = {};
            var attributes = {href: 'javascript:void()'};
            var attributesToClean = [];
            var editor = this.getParentEditor();
            data.link = {};

            this.commitContent(data);

            var addOrRemoveAttribute = function(key, value) {
                if (value) {
                    attributes[key] = value;
                } else {
                    attributesToClean.push(value);
                };
            };

            addOrRemoveAttribute('target', data.link.target);
            addOrRemoveAttribute('title', data.link.title);
            addOrRemoveAttribute('silva_anchor', data.link.anchor);

            switch (data.link.type) {
            case 'intern':
                attributes.silva_target = data.link.content;
                break;
            case 'extern':
                attributes.href = data.link.url;
                attributesToClean.push('silva_reference');
                attributesToClean.push('silva_target');
                break;
            };

            var element = CKEDITOR.plugins.silvalink.getSelectedLink(editor);

            if (element == null) {
                if (data.link.type == 'intern') {
                    attributes.silva_reference = 'new';
                };
                CKEDITOR.plugins.silvalink.insertAndSelectTextIfNoneSelected(
                    editor, data.link.title || data.link.url);

                var style = new CKEDITOR.style({element: 'a', attributes: attributes});

                style.type = CKEDITOR.STYLE_INLINE;
                style.apply(editor.document);
            } else {
                element.setAttributes(attributes);
                element.removeAttributes(attributesToClean);
            };
        }
    };
});
