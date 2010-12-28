

CKEDITOR.dialog.add('silvaimage', function(editor) {

    return {
        title: 'Image properties',
        minWidth: 350,
        minHeight: 230,
        contents: [
            { id: 'image',
              label: 'Image',
              elements: [
                  { type: 'radio',
                    id: 'type',
                    label: 'Image type',
                    items: [
                        ['internal image', 'intern'],
                        ['external image', 'extern']
                    ],
                    required: true,
                    onChange: function() {
                        var value = this.getValue();
                        var dialog = this.getDialog();
                        var urlField = dialog.getContentElement('image', 'url').getElement();
                        var referenceField = dialog.getContentElement('image', 'imageContent').getElement();

                        if (value == 'intern') {
                            urlField.hide();
                            referenceField.show();
                        } else {
                            referenceField.hide();
                            urlField.show();
                        }
                    },
                    setup: function(data) {
                        this.setValue(data.image.type);
                    },
                    commit: function(data) {
                        data.image.type = this.getValue();
                    }
                  },
                  { type: 'text',
                    id: 'url',
                    label: 'Image URL',
                    required: true,
                    setup: function(data) {
                        this.setValue(data.image.url);
                    },
                    commit: function(data) {
                        data.image.url = this.getValue();
                    }
                  },
                  { type: 'reference',
                    id: 'imageContent',
                    label: 'Image',
                    content: 'silva.core.interfaces.content.IImage',
                    required: true,
                    setup: function(data) {
                        if (data.image.content != undefined) {
                            this.setValue(data.image.content);
                        } else {
                            this.clear();
                        };
                    },
                    commit: function(data) {
                        data.image.content = this.getValue();
                    }
                  },
                  { type: 'select',
                    id: 'align',
                    label: 'Image alignement',
                    required: true,
                    items: [
                        ['default', 'default'],
                        ['align left', 'image-left'],
                        ['align center', 'image-center'],
                        ['align right', 'image-right'],
                        ['float left', 'float-left'],
                        ['float right', 'float-right']
                    ],
                    setup: function(data) {
                        this.setValue(data.image.align);
                    },
                    commit: function(data) {
                        data.image.align = this.getValue();
                    }
                  },
                  { type: 'text',
                    id: 'alt',
                    label: 'Image alternative text',
                    required: false,
                    setup: function(data) {
                        this.setValue(data.image.alt);
                    },
                    commit: function(data) {
                        data.image.alt = this.getValue();
                    }
                  },
                  { type: 'text',
                    id: 'caption',
                    label: 'Image caption',
                    required: false,
                    setup: function(data) {
                        this.setValue(data.image.caption);
                    },
                    commit: function(data) {
                        var dialog = this.getDialog();
                        var altAsCaption = dialog.getContentElement('image', 'altAsCaption').getValue();

                        if (altAsCaption) {
                            var alt = dialog.getContentElement('image', 'alt').getValue();

                            data.image.caption = alt;
                        } else {
                            data.image.caption = this.getValue();
                        };
                    }
                  },
                  { type: 'checkbox',
                    id: 'altAsCaption',
                    label: 'Use image alternative text as caption',
                    required: false,
                    onChange: function() {
                        var value = this.getValue();
                        var dialog = this.getDialog();
                        var caption = dialog.getContentElement('image', 'caption').getElement();

                        if (value) {
                            caption.hide();
                        } else {
                            caption.show();
                        }
                    },
                    setup: function(data) {
                        var value = data.image.alt == data.image.caption;
                        this.setValue(value);
                    }
                    // Commit is done in caption field
                  }
              ]
            },
            { id: 'link',
              label: 'Link',
              elements: [
                  { type: 'checkbox',
                    id: 'linkHires',
                    label: 'Link to the hires version of the image',
                    required: false,
                    onChange: function() {
                        var value = this.getValue();
                        var dialog = this.getDialog();
                        var options = dialog.getContentElement('link', 'linkOptions').getElement();

                        if (value) {
                            options.hide();
                        } else {
                            options.show();
                        }
                    }
                  },
                  { type: 'vbox',
                    id: 'linkOptions',
                    children: CKEDITOR.plugins.silvalink.createDialogFields()
                  }
              ]
            }
        ],
        onShow: function() {
            var data = {};

            data.link = {};
            data.link.type = 'intern';
            data.image = {};
            data.image.type = 'intern';
            this.setupContent(data);
        }
    };
});
