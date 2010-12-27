
(function ($) {
    CKEDITOR.dialog.add('silvalink', function(editor) {

        var typeChanged = function () {
            var dialog = this.getDialog();
            var type = dialog.getContentElement('link', 'type').getValue();
            var urlField = dialog.getContentElement('link', 'url').getElement();
            var referenceField = dialog.getContentElement('link', 'referredContent').getElement();
            var documentAnchor = dialog.getContentElement('link', 'documentAnchor').getElement();
            var anchor = dialog.getContentElement('link', 'anchor').getElement();

            if (type == 'intern') {
                urlField.hide();
                documentAnchor.hide();
                referenceField.show();
                anchor.show();
            } else if (type == 'extern') {
                referenceField.hide();
                documentAnchor.hide();
                urlField.show();
                anchor.show();
            } else {
                urlField.hide();
                referenceField.hide();
                anchor.hide();
                documentAnchor.show();
            };
        };

        var targetChanged = function() {
            var dialog = this.getDialog();
            var target = dialog.getContentElement('link', 'target');
            var input = dialog.getContentElement('link', 'customTarget');
            if (target.getValue() == 'input') {
                input.getElement().show();
            } else {
                input.getElement().hide();
            };
        };

        return {
            title: 'Link to a content',
            minWidth: 350,
            minHeight: 230,
            contents: [
                { id: 'link',
                  elements: [
                      { type: 'radio',
                        id: 'type',
                        label: 'Link type',
                        items: [['internal link', 'intern'],
                                ['external link', 'extern'],
                                ['anchor', 'anchor']
                               ],
                        onChange: typeChanged,
                        required: true,
                        setup: function(data) {
                            this.setValue(data.type);
                        },
                        commit: function(data) {
                            data.type = this.getValue();
                        }
                      },
                      { type: 'text',
                        id: 'url',
                        label: 'External URL',
                        hidden: true,
                        required: true,
                        setup: function(data) {
                            this.setValue(data.url);
                        },
                        commit: function(data) {
                            data.url = this.getValue();
                        }
                      },
                      { type: 'reference',
                        id: 'referredContent',
                        label: 'Link target',
                        required: true,
                        setup: function(data) {
                            if (data.referredContent != undefined) {
                                this.setValue(data.referredContent);
                            } else {
                                this.clear();
                            };
                        },
                        commit: function(data) {
                            data.referredContent = this.getValue();
                        }
                      },
                      { type: 'select',
                        id: 'documentAnchor',
                        label: 'Anchor',
                        items: [],
                        hidden: true,
                        required: true,
                        setup: function(data) {
                            var anchors = new CKEDITOR.dom.nodeList(editor.document.$.anchors);

                            this.clear();
                            for (var i=0; i < anchors.count(); i++ ) {
                                this.add(anchors.getItem(i).getAttribute('name'));
                            };
                        }
                      },
                      { type: 'text',
                        id: 'anchor',
                        label: 'Anchor',
                        required: true,
                        commit: function(data) {
                            data.anchor = this.getValue();
                        }
                      },
                      { type: 'select',
                        id: 'target',
                        label: 'Window target',
                        items: [['same window', '_self'],
                                ['new window', '_blank'],
                                ['parent', '_parent'],
                                ['top', '_top'],
                                ['custom target', 'input']
                               ],
                        onChange: targetChanged,
                        required: true,
                        setup: function(data) {
                            var isCustom = true;
                            var items = this._.select.items;

                            for (var i = 0; i < items.length; i++) {
                                if (items[i][1] == data.target) {
                                    isCustom = false;
                                    break;
                                };
                            };
                            if (isCustom) {
                                var customTarget = this.getDialog().getContentElement('link', 'customTarget');

                                customTarget.setValue(data.target);
                                this.setValue('input');
                            } else {
                                this.setValue(data.target);
                            }
                        },
                        commit: function(data) {
                            var target = this.getValue();

                            if (target == 'input') {
                                var customTarget = this.getDialog().getContentElement('link', 'customTarget');

                                target = customTarget.getValue();
                            }
                            data.target = target;
                        }
                      },
                      { type: 'text',
                        id: 'customTarget',
                        label: 'Custom target',
                        hidden: true,
                        required: true
                        // Setup and commit are done by the target field.
                      },
                      { type: 'text',
                        id: 'title',
                        label: 'Link title',
                        setup: function(data) {
                            this.setValue(data.title);
                        },
                        commit: function(data) {
                            data.title = this.getValue();
                        }
                      }
                 ]
                }
            ],
            onShow: function() {
                var data = {};
                var editor = this.getParentEditor();
                var element = CKEDITOR.plugins.silvalink.getSelectedLink(editor);
                if (element != null) {
                    // Read and load link information
                    var link = element.$;
                    var href = link.getAttribute('href');
                    data.title = link.getAttribute('title');
                    data.target = link.getAttribute('target');
                    if (link.hasAttribute('silva_reference')) {
                        data.type = 'intern';
                        data.referredContent = link.getAttribute(
                            'silva_target');
                    } else {
                        data.type = 'extern';
                        data.url = link.getAttribute('href');
                    };
                } else {
                    // Default values, there are no link here
                    data.type = 'intern';
                };
                this.setupContent(data);
            },
            onOk: function() {
                var data = {};

                this.commitContent(data);
                console.log(data);
                alert("Ok !!!");
            }
        };
    });
})(jQuery);
