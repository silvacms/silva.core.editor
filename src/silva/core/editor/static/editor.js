

(function($, infrae, CKEDITOR) {
    infrae.interfaces.register('editor');

    // There are two settings registry, one used for full mode, one used then embded (like inside a form).
    var MODULE_BLACKLIST = ['save', 'link', 'flash', 'image' , 'filebrowser', 'iframe','forms'],
        FULL_SETTINGS = [],
        EMBDED_SETTINGS = [];

    $(document).bind('load-smiplugins', function(event, smi) {

        var build_settings = function(configuration, embded) {
            // Create settings out of the configuration that is fetched from the server.
            var plugins_blacklist = MODULE_BLACKLIST.slice(),
                plugins_extra = configuration['plugins'];

            if (embded) {
                // In embded mode we remove the save plugin.
                var index = $.inArray('silvasave', plugins_extra);

                plugins_blacklist.push('silvasave');
                if (index > -1) {
                    plugins_extra.splice(index, 1);
                };
            };
            var settings = {
                entities: false,
                fullPage: false,
                basicEntities: true,
                language: smi.get_language(),
                contentsCss: configuration['contents_css'],
                silvaFormats: configuration['formats'],
                silvaTableStyles: configuration['table_styles'],
                extraPlugins: plugins_extra.join(','),
                removePlugins: plugins_blacklist.join(','),
                toolbar: 'Silva',
                toolbar_Silva: configuration['toolbars'],
                height: '2000px',
                resize_enabled: false,
                disable_colors: configuration['disable_colors'],
                startupShowBorders: configuration['startup_show_borders'],
                bodyClass: configuration['editor_body_class'],
                dialog_buttonsOrder: 'rtl'
            };
            if (configuration['skin']) {
                settings['skin'] = configuration['skin'];
            };
            return settings;
        };

        var get_settings = function(name, embded) {
            var registry = embded ? EMBDED_SETTINGS : FULL_SETTINGS;

            return registry[name] !== undefined ?
                $.when(registry[name]) :
                (function () {
                    return $.ajax({
                        url: smi.options.editor.configuration,
                        dataType: 'json',
                        data: [{name: 'name', value: name}]
                    }).then(function(configuration) {
                        for (var key in configuration['paths']) {
                            CKEDITOR.plugins.addExternal(key, configuration['paths'][key]);
                        };
                        // Create and register the settings for reuse later on.
                        FULL_SETTINGS[name] = build_settings(configuration, false);
                        EMBDED_SETTINGS[name] = build_settings(configuration, true);
                        return registry[name];
                    }, function(request) {
                        return $.Deferred().reject(request);
                    });
                })();
        };

        // This is used by the form field (the editor is embded)
        var create_html_field = function(data) {
            var $textarea = $(this);

            get_settings($textarea.data('editor-configuration'), true).done(function(settings) {
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
                data.container.bind('clean-smiform', function () {
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

        $(document).on('loadwidget-smiform', '.form-fields-container', function(event, data) {
            $(this).find('.field-htmltext').each(function () {
                create_html_field.call(this, data);
            });
            event.stopPropagation();
        });

        // This is the full size editor screen (the editor is full).
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
                                    // This URL should be configurable ...
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
