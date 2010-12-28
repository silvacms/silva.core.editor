

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
                var href = link.getAttribute('href');
                data.link.title = link.getAttribute('title');
                data.link.target = link.getAttribute('target');
                if (link.hasAttribute('silva_reference')) {
                    data.link.type = 'intern';
                    data.link.content = link.getAttribute(
                        'silva_target');
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
            data.link = {};

            this.commitContent(data);
            console.log(data);
            alert("Ok !!!");
        }
    };
});
