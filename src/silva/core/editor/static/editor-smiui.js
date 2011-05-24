

(function($, infrae, CKEDITOR) {

    infrae.interfaces.register('editor');

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
                    removePlugins: 'save,link,flash,image,filebrowser,iframe,forms',
                    toolbar: 'Silva',
                    height: '2000px',
                    toolbar_Silva: configuration['toolbars'],
                    resize_enabled: false
                };
                if (configuration['skin']) {
                    settings['skin'] = configuration['skin'];
                };

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
                                        'Do you want to continue?'});
                            };
                            return null;
                        };

                        return {
                            jsont: '<textarea name="{data.name|htmltag}">{data.text}</textarea>',
                            render: function() {
                                var textarea = $content.children('textarea').get(0);
                                var resize = function () {
                                    // XXX Where the hell comes from those 5 pixels ?
                                    var height = $content.height() - 5;

                                    height -= $('#cke_top_body').outerHeight();
                                    height -= $('#cke_bottom_body').outerHeight();
                                    editor.resize(editor.container.getStyle('width'), height, true);
                                };

                                editor = CKEDITOR.replace(textarea, settings);
                                editor.on('instanceReady', resize);
                                editor.on('instanceReady', function() {
                                    $(window).bind('resize.smi-editor', resize);
                                });
                            },
                            cleanup: function() {
                                $(window).unbind('resize.smi-editor');
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
