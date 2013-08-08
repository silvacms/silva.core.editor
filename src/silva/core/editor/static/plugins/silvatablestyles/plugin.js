

CKEDITOR.plugins.add('silvatablestyles', {
    requires: ['richcombo'],
    init : function (editor) {
        var table_styles = editor.config.silvaTableStyles;

        editor.ui.addRichCombo('SilvaTableStyles', {
            label: 'Table styles',
            title: 'Table styles',
            className: 'cke_table_style',
            panel: {
                css: editor.skin.editor.css.concat(editor.config.contentsCss),
                multiSelect: false
            },
            init: function () {
                this.startGroup('Table styles');
                var id = null;
                var table_style = null;

                for (var i=0; i < table_styles.order.length; i++) {
                    id = table_styles.order[i];
                    table_style = table_styles[id];

                    this.add(id, table_style.name, table_style.name);
                }
            },
            onClick: function(value) {

                editor.focus();
                editor.fire('saveSnapshot');

                var selected = CKEDITOR.silva.utils.getSelectedElement(editor);

                while (selected !== null && selected.getName() !== 'table' ) {
                   selected = selected.getParent();
                }

                if (selected !== null && selected.getName() === 'table') {
                    var id = null;
                    var table_style_class = null;

                    for (var i=0; i < table_styles.order.length; i++) {
                        id = table_styles.order[i];
                        table_style_class = table_styles[id].html_class;

                        selected.removeClass(table_style_class);
                    }
                    selected.addClass(table_styles[value].html_class);
                }

                setTimeout(function() {
                    editor.fire('saveSnapshot');
                }, 0 );
            },
            onRender: function() {

                editor.on('selectionChange', function()  {
                    var selected = CKEDITOR.silva.utils.getSelectedElement(editor);

                    while (selected !== null && selected.getName() !== 'table' ) {
                       selected = selected.getParent();
                    }

                    if (selected !== null && selected.getName() === 'table') {

                        $('#cke_'+ this.id).show(500);

                        var id = null;
                        var table_style = null;

                        for (var i=0; i < table_styles.order.length; i++) {
                            id = table_styles.order[i];
                            table_style = table_styles[id];

                            if (selected.hasClass(table_style.html_class)) {
                                this.setValue(id, table_style.name);
                                return;
                            }
                        }
                        var default_table_style = table_styles[table_styles.order[0]];
                        selected.addClass(default_table_style.html_class);
                        this.setValue(table_styles.order[0], default_table_style.name);
                    }
                    else {
                        this.setValue('');
                        $('#cke_'+ this.id).hide(500);
                    }
                }, this);
            }
        });
    }
});
