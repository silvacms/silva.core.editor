

(function($, infrae, CKEDITOR) {

    infrae.interfaces.register('editor');

    var MODULE_BLACKLIST = ['save', 'link', 'flash', 'image' , 'filebrowser', 'iframe','forms'];
    var configurations = [];

    $(document).bind('load-smiplugins', function(event, smi) {

        var get_settings = function(name) {
            return configurations[name] !== undefined ?
                $.when(configurations[name]) :
                (function () {
                    return $.ajax({
                        url: smi.options.editor.configuration,
                        dataType: 'json',
                        data: [{name: 'name', value: name}]
                    }).pipe(function(configuration) {
                        for (var key in configuration['paths']) {
                            CKEDITOR.plugins.addExternal(key, configuration['paths'][key]);
                        };

                        var settings = {
                            entities: false,
                            fullPage: false,
                            basicEntities: true,
                            language: smi.get_language(),
                            contentsCss: configuration['contents_css'],
                            silvaFormats: configuration['formats'],
                            extraPlugins: configuration['plugins'],
                            removePlugins: MODULE_BLACKLIST.join(','),
                            toolbar: 'Silva',
                            height: '2000px',
                            toolbar_Silva: configuration['toolbars'],
                            resize_enabled: false,
                            disable_colors: configuration['disable_colors'],
                            dialog_buttonsOrder: 'rtl'
                        };
                        if (configuration['skin']) {
                            settings['skin'] = configuration['skin'];
                        };
                        configurations[name] = settings;
                        return settings;
                    }, function(request) {
                        return $.Deferred().reject(request);
                    });
                })();
        };

        // This is used by the form field.
        var create_html_field = function(data) {
            var $textarea = $(this);

            get_settings($textarea.data('editor-configuration')).done(function(settings) {
                var editor = CKEDITOR.replace(
                    $textarea.get(0), $.extend({}, settings, {height: '300px'}));

                editor.on('instanceReady', function() {
                    if (data.popup !== undefined) {
                        infrae.ui.ResizeDialog(data.popup);
                    };
                });
                data.form.bind('serialize-smiform', function () {
                    $textarea.val(editor.getData());
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
                            message:'This document has been modified. ' +
                                'If you continue you will lose these modifications. ' +
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
                    jsont: '<textarea name="{data.name|htmltag}">{data.text|html}</textarea>',
                    render: function() {
                        return get_settings(data.configuration).done(function(settings) {
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
    });
})(jQuery, infrae, CKEDITOR);
