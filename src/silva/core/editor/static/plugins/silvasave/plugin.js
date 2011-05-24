(function($) {
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
                            if (data['status'] == 'success') {
                                $(document).trigger('refresh-feedback-smi');
                                if (data[editor.name] != undefined) {
                                    editor.setData(data[editor.name], function() {
                                        // We document is no longer modified.
                                        this.resetDirty();
                                    });
                                };
                            } else {
                                var message = 'Error while saving document';
                                if (data['alert']) {
                                    message += ': ' + data['alert'];
                                };
                                alert(message);
                            };
                        },
                        error: function() {
                            alert('Error on the server while saving document, ' +
                                  'Please consult log server for detail');
                        }
                    });
                }
            });
            editor.ui.addButton('SilvaSave', {
                label: editor.lang.save,
                command: 'silvasave',
                className: 'cke_button_save'
            });
        }
    });
})(jQuery);
