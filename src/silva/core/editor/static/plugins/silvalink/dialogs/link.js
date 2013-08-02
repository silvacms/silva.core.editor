

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
                data.link.anchor = link.getAttribute('data-silva-anchor');
                if (link.hasAttribute('data-silva-reference')) {
                    data.link.type = 'intern';
                    data.link.content = link.getAttribute('data-silva-target');
                } else {
                    var href = link.getAttribute('data-silva-url');

                    if (!href || href == 'javascript:void(0)') {
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
            var attributes = {href: 'javascript:void(0)'};
            var attributes_to_clean = [];
            var editor = this.getParentEditor();
            var element = CKEDITOR.plugins.silvalink.getSelectedLink(editor);

            attributes['class'] = 'link';
            data.link = {};
            this.commitContent(data);

            var update_attribute = function(key, value) {
                if (value) {
                    attributes[key] = value;
                } else {
                    attributes_to_clean.push(key);
                };
            };

            update_attribute('target', data.link.target);
            update_attribute('title', data.link.title);
            update_attribute('data-silva-anchor', data.link.anchor);

            switch (data.link.type) {
            case 'intern':
                attributes['data-silva-target'] = data.link.content;
                if (element == null || !element.hasAttribute('data-silva-reference')) {
                    attributes['data-silva-reference'] = 'new';
                };
                attributes_to_clean.push('data-silva-url');
                break;
            case 'extern':
                // We save the value into data-silva-url. We set the href
                // attribute to get the link underlined.
                attributes['href'] = 'javascript:void(0)';
                attributes['data-silva-url'] = data.link.url;
                attributes_to_clean.push('data-silva-reference');
                attributes_to_clean.push('data-silva-target');
                break;
            case 'anchor':
                attributes_to_clean.push('data-silva-url');
                attributes_to_clean.push('data-silva-reference');
                attributes_to_clean.push('data-silva-target');
                break;
            };

            if (element == null) {
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
