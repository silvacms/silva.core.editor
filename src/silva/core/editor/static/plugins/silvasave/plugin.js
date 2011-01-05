CKEDITOR.plugins.add('silvasave', {
    init: function(editor) {
        editor.addCommand('silvasave', {
            exec: function(editor) {
                var url =  $('#content-url').attr('href') + '/++rest++silva.core.editor.save';
                var data = {};

                data[editor.name] = editor.getData();
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: data,
                    success: function(data) {
                        if (data[editor.name] != undefined) {
                            editor.setData(data[editor.name]);
                        };
                    },
                    error: function() {
                        alert('You lost all your work. Courage ! This was only the beginning.');
                    }
                });
            }
        });
        editor.ui.addButton('SilvaSave', {
            label: 'editor.plugin.save',
            command: 'silvasave',
            className: 'cke_button_save'
        });
    }
});
