

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

                        switch (value) {
                        case 'intern':
                            urlField.hide();
                            referenceField.show();
                            break;
                        case 'extern':
                            referenceField.hide();
                            urlField.show();
                            break;
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
                    validate: function() {
                        var dialog = this.getDialog();
                        var type = dialog.getContentElement('image', 'type').getValue();

                        if (type == 'extern') {
                            var checker = CKEDITOR.dialog.validate.regex(
                                /^(?:http|https):\/\/.*$/,
                                'You need a specify a valid image external URL !');

                            return checker.apply(this);
                        };
                        return true;
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
                    onReferenceUpdate: function(event) {
                        var dialog = this.getDialog();
                        var alt = dialog.getContentElement('image', 'alt');
                        var url = dialog.getContentElement('image', 'url');

                        if (!alt.getValue()) {
                            alt.setValue(event.data.title);
                        };
                        url.setValue(event.data.url);
                    },
                    setup: function(data) {
                        if (data.image.content != undefined) {
                            this.setValue(data.image.content);
                        } else {
                            this.clear();
                        };
                    },
                    validate: function() {
                        var dialog = this.getDialog();
                        var type = dialog.getContentElement('image', 'type').getValue();

                        if (type == 'intern') {
                            var checker = CKEDITOR.dialog.validate.notEmpty(
                                'You need to select an image to insert !');

                            return checker.apply(this);
                        };
                        return true;
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
                        var custom = dialog.getContentElement('link', 'linkCustom');

                        if (value) {
                            custom.setValue(false);
                        }
                    },
                    setup: function(data) {
                        this.setValue(data.link.hires);
                    },
                    commit: function(data) {
                        data.link.hires = this.getValue();
                    }
                  },
                  { type: 'checkbox',
                    id: 'linkCustom',
                    label: 'Link to an another content',
                    required: false,
                    onChange: function() {
                        var value = this.getValue();
                        var dialog = this.getDialog();
                        var hires = dialog.getContentElement('link', 'linkHires');
                        var options = dialog.getContentElement('link', 'linkCustomOptions').getElement();

                        if (value) {
                            hires.setValue(false);
                            options.show();
                        } else {
                            options.hide();
                        };
                    },
                    setup: function(data) {
                        if (data.link.type != null) {
                            this.setValue(true);
                        } else {
                            this.setValue(false);
                        };
                    }
                  },
                  { type: 'vbox',
                    id: 'linkCustomOptions',
                    children: CKEDITOR.plugins.silvalink.createDialogFields(function (validator) {
                        return function () {
                            var dialog = this.getDialog();
                            var activated = dialog.getContentElement('link', 'linkCustom').getValue();

                            if (activated) {
                                return validator.apply(this);
                            }
                            return true;
                        };
                    })
                  }
              ]
            }
        ],
        onShow: function() {
            var data = {};
            var editor = this.getParentEditor();
            var element = CKEDITOR.plugins.silvaimage.getSelectedImage(editor);

            data.link = {};
            data.image = {};
            if (element != null) {
                alert('foo !');
            }
            data.image.type = 'intern';
            this.setupContent(data);
        },
        onOk: function() {
            var data = {};
            var editor =  this.getParentEditor();

            data.link = {};
            data.image = {};
            this.commitContent(data);

            var selection = editor.getSelection();
            var ranges = selection.getRanges(true);

            var div = new CKEDITOR.dom.element('div');
            var div_attributes = {contenteditable: false};
            ranges[0].insertNode(div);
            selection.selectElement(div);
            div_attributes['class'] = 'image';
            div.setAttributes(div_attributes);
            div.addClass(data.image.align);
            div.unselectable();
            var a = new CKEDITOR.dom.element('a');
            var a_attributes = {href: 'javascript:void()'};
            if (data.link.type) {
                a_attributes['target'] = data.link.target;
                a_attributes['title'] = data.link.title;
                switch (data.link.type) {
                case 'intern':
                    a_attributes['silva_target'] = data.link.content;
                    a_attributes['silva_reference'] = 'new';
                    break;
                case 'extern':
                    a_attributes['href'] = data.link.url;
                    break;
                };
            };
            a.setAttributes(a_attributes);
            div.append(a);
            var img = new CKEDITOR.dom.element('img');
            var img_attributes = {src: data.image.url,
                                  alt: data.image.alt};
            if (data.image.type == 'intern') {
                img_attributes['silva_target'] = data.image.content;
                img_attributes['silva_reference'] = 'new';
            };
            img.setAttributes(img_attributes);
            a.append(img);
            if (data.image.caption) {
                var caption = new CKEDITOR.dom.element('span');
                var caption_attributes = {};
                caption_attributes['class'] = 'caption';
                caption.setAttributes(caption_attributes);
                caption.setText(data.image.caption);
                a.append(caption);
            }
        }
    };
});
