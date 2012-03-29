

(function($, infrae, CKEDITOR) {

    infrae.interfaces.register('editor');

    var MODULE_BLACKLIST = ['save', 'link', 'flash', 'image' , 'filebrowser', 'iframe','forms'];

    $(document).bind('load-smiplugins', function(event, smi) {
        $.ajax({
            url: smi.options.editor.configuration,
            async: false,
            dataType: 'json',
            success:function(configuration) {

                for (var name in configuration['paths']) {
                    CKEDITOR.plugins.addExternal(name, configuration['paths'][name]);
                };
                var settings = {
                    entities: false,
                    fullPage: false,
                    language: smi.get_language(),
                    contentsCss: configuration['contents_css'],
                    silvaFormats: configuration['formats'],
                    extraPlugins: configuration['plugins'],
                    removePlugins: MODULE_BLACKLIST.join(','),
                    toolbar: 'Silva',
                    height: '2000px',
                    toolbar_Silva: configuration['toolbars'],
                    resize_enabled: false,
                    disable_colors: configuration['disable_colors']
                };
                if (configuration['skin']) {
                    settings['skin'] = configuration['skin'];
                };

                // This is used by the form field.
                var create_html_field = function(data) {
                    var editor = CKEDITOR.replace(this, $.extend({}, settings, {height: '300px'}));
                    var textarea = $(this);

                    editor.on('instanceReady', function() {
                        if (data.popup !== undefined) {
                            infrae.ui.ResizeDialog(data.popup);
                        };
                    });
                    data.form.bind('serialize-smiform', function () {
                        textarea.val(editor.getData());
                    });
                    data.form.bind('clean-smiform', function () {
                        try {
                            editor.destroy(true);
                        } catch(error) {
                            if (window.console && console.log) {
                                console.log('Error while destroying field editor', error);
                            };
                        };
                    });
                };

                $('.form-fields-container').live('loadwidget-smiform', function(event, data) {
                    $(this).find('.field-htmltext').each(function () {
                        create_html_field.call(this, data);
                    });
                    event.stopPropagation();
                });

                // This is the full size editor screen (no form).
                infrae.views.view({
                    iface: 'editor',
                    name: 'content',
                    factory: function($content, data, smi) {
                        var editor = null;

                        smi.objection = function () {
                            if (editor != null && editor.checkDirty()) {
                                return infrae.ui.ConfirmationDialog({
                                    title: 'Modifications',
                                    message:'This document have been modified. ' +
                                        'If you continue you will loose thoses modifications. ' +
                                        'Do you want to continue?',
                                    buttons: {
                                        Save: function() {
                                            var url =  $('#content-url').attr('href') +
                                                '/++rest++silva.core.editor.save';
                                            var data = {};

                                            data[editor.name] = editor.getData();
                                            return $.ajax({
                                                url: url,
                                                type: 'POST',
                                                data: data});
                                        },
                                        Discard: function() {
                                            return true;
                                        },
                                        Cancel: function() {
                                            return false;
                                        }
                                    }});
                            };
                            return null;
                        };

                        return {
                            jsont: '<textarea name="{data.name|htmltag}">{data.text}</textarea>',
                            render: function() {
                                var textarea = $content.children('textarea').get(0);
                                var resize = function () {
                                    var height = $content.innerHeight() - 4;
                                    var width = $content.innerWidth();

                                    editor.resize(width, height);
                                };

                                editor = CKEDITOR.replace(textarea, settings);
                                editor.on('instanceReady', resize);
                                editor.on('instanceReady', function() {
                                    $(window).bind('resize.smi-editor', resize);
                                    $(window).bind('workspace-resize-smi.smi-editor', resize);
                                });
                            },
                            cleanup: function() {
                                $(window).unbind('resize.smi-editor');
                                $(window).unbind('workspace-resize-smi.smi-editor');
                                $content.empty();
                                if (editor != null) {
                                    try {
                                        editor.destroy(true);
                                        editor = null;
                                    } catch(error) {
                                        if (window.console && console.log) {
                                            console.log('Error while destroying editor', error);
                                        };
                                    };
                                }
                            }
                        };
                    }
                });
            }
        });
    });
})(jQuery, infrae, CKEDITOR);
