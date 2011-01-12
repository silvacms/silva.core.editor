

// createDialogFields is defined in plugin.js as it is used by other
// plugins

CKEDITOR.dialog.add('silvalink', function(editor) {

    return {
        title: 'Link properties',
        minWidth: 350,
        minHeight: 230,
        contents: [
            { id: 'link',
              elements: CKEDITOR.plugins.silvalink.createDialogFields(null)
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
                data.link.anchor = link.getAttribute('_silva_anchor');
                if (link.hasAttribute('_silva_reference')) {
                    data.link.type = 'intern';
                    data.link.content = link.getAttribute('_silva_target');
                } else {
                    var href = link.getAttribute('_silva_href');

                    if (href == 'javascript:void()') {
                        data.link.type = 'anchor';
                    } else {
                        data.link.type = 'extern';
                        data.link.url = href;
                    };
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
            var attributes_to_clean = [];
            var editor = this.getParentEditor();

            attributes['class'] = 'link';
            data.link = {};
            this.commitContent(data);

            var addOrRemoveAttribute = function(key, value) {
                if (value) {
                    attributes[key] = value;
                } else {
                    attributes_to_clean.push(key);
                };
            };

            addOrRemoveAttribute('target', data.link.target);
            addOrRemoveAttribute('title', data.link.title);
            addOrRemoveAttribute('_silva_anchor', data.link.anchor);

            switch (data.link.type) {
            case 'intern':
                attributes['_silva_target'] = data.link.content;
                attributes_to_clean.push('_silva_href');
                break;
            case 'extern':
                // We save the value into _silva_href. We set the href
                // attribute to get the link underlined.
                attributes['href'] = data.link.url;
                attributes['_silva_href'] = data.link.url;
                attributes_to_clean.push('_silva_reference');
                attributes_to_clean.push('_silva_target');
                break;
            case 'anchor':
                attributes_to_clean.push('_silva_href');
                attributes_to_clean.push('_silva_reference');
                attributes_to_clean.push('_silva_target');
                break;
            };

            var element = CKEDITOR.plugins.silvalink.getSelectedLink(editor);

            if (element == null) {
                if (data.link.type == 'intern') {
                    attributes['_silva_reference'] = 'new';
                };
                CKEDITOR.plugins.silvalink.insertAndSelectTextIfNoneSelected(
                    editor, data.link.title || data.link.url);

                var style = new CKEDITOR.style({element: 'a', attributes: attributes});

                style.type = CKEDITOR.STYLE_INLINE;
                style.apply(editor.document);
            } else {
                element.setAttributes(attributes);
                element.removeAttributes(attributes_to_clean);
            };
        }
    };
});
