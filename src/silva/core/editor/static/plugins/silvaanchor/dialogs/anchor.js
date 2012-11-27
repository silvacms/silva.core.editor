
(function(){
    var API = CKEDITOR.plugins.silvaanchor;
    var validate = CKEDITOR.dialog.validate;

    CKEDITOR.dialog.add('silvaanchor', function(editor) {

        return {
            title: 'Anchor properties',
            minWidth: 350,
            minHeight: 130,
            contents: [
                { id: 'anchor',
                  elements: [
                      { type: 'text',
                        id: 'name',
                        label: 'Anchor name',
                        required: true,
                        setup: function(data) {
                            this.setValue(data.anchor.name);
                        },
                        validate: function(data) {
                            var checker = validate.notEmpty('Missing anchor name');

                            return checker.apply(this);
                        },
                        commit: function(data) {
                            data.anchor.name = this.getValue();
                        }
                      },
                      { type: 'text',
                        id: 'title',
                        label: 'Index title',
                        setup: function(data) {
                            this.setValue(data.anchor.title);
                        },
                        commit: function(data) {
                            data.anchor.title = this.getValue();
                        }
                      }
                  ]
                }
            ],
            onShow: function() {
                var data = {};
                var editor =  this.getParentEditor();
                var element = API.getSelectedAnchor(editor);

                data.anchor = {};
                if (element != null) {
                    var anchor = element.$;
                    data.anchor.title = anchor.getAttribute('title');
                    data.anchor.name = anchor.getAttribute('name');
                }
                this.setupContent(data);
            },
            onOk: function() {
                var data = {};
                var editor =  this.getParentEditor();
                var element = API.getSelectedAnchor(editor);

                data.anchor = {};
                this.commitContent(data);

                var attributes = { contenteditable: 'false',
                                   name: data.anchor.name };
                attributes['data-cke-saved-name'] = data.anchor.name;
                if (data.anchor.title) {
                    attributes['title'] = data.anchor.title;
                };

                var text = API.getAnchorTextFromAttributes(attributes);

                attributes['class'] = 'anchor';
                if (element == null) {
                    var selection = editor.getSelection();
                    var ranges = selection.getRanges();

                    element = new CKEDITOR.dom.element('a');
                    ranges[0].insertNode(element);
                    selection.selectElement(element);
                };
                element.setText(text);
                element.setAttributes(attributes);
            }
        };
    });
})();
