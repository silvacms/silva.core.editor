

CKEDITOR.plugins.add('silvaformat', {
    requires: ['richcombo', 'styles'],
    init : function(editor) {
        var lang = editor.lang.format;
        var formats = editor.config.silvaFormats;

        // Create style objects for all defined styles.
        for (var i=0; i < formats.order.length; i++) {
            var identifier = formats.order[i];
            var format = formats[identifier];

            format.style = new CKEDITOR.style(format);
            format.style._.enterMode = editor.config.enterMode;
        }

        editor.ui.addRichCombo('SilvaFormat', {
            label: lang.label,
            title: lang.panelTitle,
            className: 'cke_format',
            panel: {
                css: editor.skin.editor.css.concat(editor.config.contentsCss),
                multiSelect: false,
                attributes: {
                    'aria-label': lang.panelTitle
                }
            },
            init: function() {
                this.startGroup(lang.panelTitle);

                for (var i=0; i < formats.order.length; i++) {
                    var identifier = formats.order[i];
                    var format = formats[identifier];

                    this.add(
                        identifier,
                        format.style.buildPreview(),
                        format.name);
                }
            },
            onClick: function(value) {
                if (CKEDITOR.plugins.silvaimage.getSelectedImage(editor)) {
                    return;
                };

                editor.focus();
                editor.fire('saveSnapshot');

                formats[value].style.apply(editor.document);

                setTimeout(function() {
                    editor.fire('saveSnapshot');
                }, 0 );
            },
            onRender: function() {
                editor.on('selectionChange', function(event)  {
                    var value = this.getValue();
                    var element_path = event.data.path;

                    for (var i=0; i < formats.order.length; i++) {
                        var identifier = formats.order[i];
                        var format = formats[identifier];

                        if (format.style.checkActive(element_path)) {
                            if (identifier != value) {
                                this.setValue(identifier, format.name);
                            };
                            return;
                        };
                    };
                    // If no styles match, just empty it.
                    this.setValue('');
                }, this);
            }
        });
    }
});
