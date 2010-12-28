(function($) {
    CKEDITOR.plugins.add('silvareference', {
        init: function(editor) {
            var templateURL = $('#content-url').attr('href') + '/++rest++silva.core.editor.widget.reference';

            var createReferenceUI = function(referenceTemplate) {
                // Create the reference UI element with the given
                // template.
                CKEDITOR.tools.extend(CKEDITOR.ui.dialog, {
                    reference: function(dialog, elementDefinition, htmlList) {
                        var identifier = dialog.getName() + '-' + elementDefinition.id;

                        this._ = {};
                        this._.id = identifier;
                        this._.remote = new ReferencedRemoteObject(identifier);
                        var innerHTML = function() {
                            var data = {};

                            data.id = identifier;
                            if (elementDefinition.content != undefined) {
                                data.content = elementDefinition.content;
                            }
                            return referenceTemplate.expand(data);
                        };
                        CKEDITOR.ui.dialog.labeledElement.call(
                            this, dialog, elementDefinition, htmlList, innerHTML);
                    }
                }, true);
                CKEDITOR.ui.dialog.reference.prototype = CKEDITOR.tools.extend(
                    new CKEDITOR.ui.dialog.labeledElement, {
                        getInputElement: function() {
                            return CKEDITOR.document.getById(this._.remote.get_reference_input().id);
                        },
                        getValue: function() {
                            return this._.remote.reference();
                        },
                        setValue: function(value) {
                            this._.remote.fetch(value);
                        },
                        clear: function() {
                            this._.remote.clear();
                        }
                    }, true);
                CKEDITOR.dialog.addUIElement('reference', {
                    build: function(dialog, elementDefinition, output) {
                        return new CKEDITOR.ui.dialog[elementDefinition.type](
                            dialog, elementDefinition, output);
                    }
                });
            };

            // Fetch reference UI template from the server and create
            // the UI element.
            $.ajax({
                url: templateURL,
                dataType: 'html',
                success: function(template) {
                    createReferenceUI(new jsontemplate.Template(template, {}));
                }
            });
        }
    });
})(jQuery);
