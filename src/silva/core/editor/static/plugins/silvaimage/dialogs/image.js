

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
                    id: 'image_type',
                    label: 'Image type',
                    items: [
                        ['internal image', 'intern'],
                        ['external image', 'extern']
                    ],
                    required: true,
                    onChange: function() {
                        var value = this.getValue();
                        var dialog = this.getDialog();
                        var urlField = dialog.getContentElement('image', 'image_url').getElement();
                        var referenceField = dialog.getContentElement('image', 'image_content').getElement();

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
                        console.log(this.getValue());
                        data.image.type = this.getValue();
                    }
                  },
                  { type: 'text',
                    id: 'image_url',
                    label: 'Image URL',
                    required: true,
                    setup: function(data) {
                        this.setValue(data.image.url);
                    },
                    validate: function() {
                        var dialog = this.getDialog();
                        var type = dialog.getContentElement('image', 'image_type').getValue();

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
                    id: 'image_content',
                    label: 'Image',
                    content: 'silva.core.interfaces.content.IImage',
                    required: true,
                    onReferenceUpdate: function(event) {
                        var dialog = this.getDialog();
                        var alt = dialog.getContentElement('image', 'image_alt');
                        var url = dialog.getContentElement('image', 'image_url');

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
                        var type = dialog.getContentElement('image', 'image_type').getValue();

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
                    id: 'image_align',
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
                    id: 'image_alt',
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
                    id: 'image_caption',
                    label: 'Image caption',
                    required: false,
                    setup: function(data) {
                        this.setValue(data.image.caption);
                    },
                    commit: function(data) {
                        var dialog = this.getDialog();
                        var altAsCaption = dialog.getContentElement('image', 'image_altAsCaption').getValue();

                        if (altAsCaption) {
                            var alt = dialog.getContentElement('image', 'image_alt').getValue();

                            data.image.caption = alt;
                        } else {
                            data.image.caption = this.getValue();
                        };
                    }
                  },
                  { type: 'checkbox',
                    id: 'image_altAsCaption',
                    label: 'Use image alternative text as caption',
                    required: false,
                    onChange: function() {
                        var value = this.getValue();
                        var dialog = this.getDialog();
                        var caption = dialog.getContentElement('image', 'image_caption').getElement();

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
                    id: 'link_hires',
                    label: 'Link to the hires version of the image',
                    required: false,
                    onChange: function() {
                        var value = this.getValue();
                        var dialog = this.getDialog();
                        var custom = dialog.getContentElement('link', 'link_custom');

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
                    id: 'link_custom',
                    label: 'Link to an another content',
                    required: false,
                    onChange: function() {
                        var value = this.getValue();
                        var dialog = this.getDialog();
                        var hires = dialog.getContentElement('link', 'link_hires');
                        var options = dialog.getContentElement('link', 'link_options').getElement();

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
                    id: 'link_options',
                    children: CKEDITOR.plugins.silvalink.createDialogFields(function (validator) {
                        return function () {
                            var dialog = this.getDialog();
                            var activated = dialog.getContentElement('link', 'link_custom').getValue();

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
            var div = CKEDITOR.plugins.silvaimage.getSelectedImage(editor);

            data.link = {};
            data.image = {};

            var defaultSettings = function() {
                data.image.type = 'intern';
                data.link.type = null;
            };

            var parseError = function(msg, element) {
                if (window.console && console.log) {
                    console.log(msg + ": " + element.getOuterHtml());
                };
                defaultSettings();
            };

            if (div != null) {
                if (div.getChildCount() == 1) {
                    var a = div.getChild(0);

                    if (a.is('a')) {
                        data.link.title = a.$.getAttribute('title');
                        data.link.target = a.$.getAttribute('target');
                        data.link.anchor = a.$.getAttribute('silva_anchor');
                        if (a.$.hasAttribute('silva_reference')) {
                            data.link.type = 'intern';
                            data.link.content = a.$.getAttribute('silva_target');
                        } else {
                            var href = a.$.getAttribute('href');

                            if (href == 'javascript:void()') {
                                data.link.type = 'anchor';
                            } else {
                                data.link.type = 'extern';
                                data.link.url = href;
                            };
                        };

                        if (a.getChildCount()) {
                            var img = a.getChild(0);

                            if (img.is('img')) {
                                data.image.alt = img.$.getAttribute('alt');
                                data.image.url = img.$.getAttribute('src');
                                if (img.$.hasAttribute('silva_reference')) {
                                    data.image.type = 'intern';
                                    data.image.content = img.$.getAttribute('silva_target');
                                } else {
                                    data.image.type = 'extern';
                                };
                            } else {
                                parseError("Invalid image tag", img);
                            };

                            if (a.getChildCount() == 2) {
                                var caption = a.getChild(1);

                                if (caption.is('span') && caption.hasClass('caption')) {
                                    data.image.caption = caption.getText();
                                } else {
                                    parseError("Invalid image caption", caption);
                                };
                            };
                        } else {
                            parseError("Invalid image link content", a);
                        };
                    } else {
                        parseError("Invalid image link", a);
                    }
                } else {
                    parseError("Invalid image structure", div);
                };
            } else {
                defaultSettings();
            };
            this.setupContent(data);
        },
        onOk: function() {
            var data = {};
            var editor =  this.getParentEditor();

            data.link = {};
            data.image = {};
            this.commitContent(data);

            var div = CKEDITOR.plugins.silvaimage.getSelectedImage(editor);
            var div_attributes = {};
            var a = null;
            var a_attributes = {};
            var a_attributes_to_clean = [];
            var img = null;
            var img_attributes = {src: data.image.url};
            var img_attributes_to_clean = [];
            var caption = null;

            // Div tag: image container
            div_attributes['class'] = 'image '+ data.image.align;
            if (div == null) {
                // We basically don't edit an image. Create a new div and select it.
                var selection = editor.getSelection();
                var ranges = selection.getRanges(true);

                div = new CKEDITOR.dom.element('div');
                div.unselectable();
                div_attributes['contenteditable'] = false;
                ranges[0].insertNode(div);
                selection.selectElement(div);
            } else {
                if (div.getChildCount() == 1) {
                    a = div.getChild(0);
                    if (!a.is('a')) {
                        a = null;
                    };
                };
                if (a == null) {
                    // Ok, we have child, but there are not links: clean them
                    for (var i=0; i < div.getChildCount();) {
                        div.getChild(0).remove();
                    };
                };
            };
            div.setAttributes(div_attributes);
            // Link tag
            if (a == null) {
                a = new CKEDITOR.dom.element('a');
                a_attributes['href'] = 'javascript:void()';
                div.append(a);
            };
            if (data.link.type) {

                var addOrRemoveAttribute = function(key, value) {
                    if (value) {
                        a_attributes[key] = value;
                    } else {
                        a_attributes_to_clean.push(key);
                    }
                };

                addOrRemoveAttribute('target', data.link.target);
                addOrRemoveAttribute('title', data.link.title);
                addOrRemoveAttribute('silva_anchor', data.link.anchor);

                switch (data.link.type) {
                case 'intern':
                    a_attributes['silva_reference'] = 'new';
                    a_attributes['silva_target'] = data.link.content;
                    break;
                case 'extern':
                    a_attributes['href'] = data.link.url;
                    // No break, clean the same attributes than anchor case
                case 'anchor':
                    a_attributes_to_clean.push('silva_reference');
                    a_attributes_to_clean.push('silva_target');
                    break;
                };
            } else {
                // No link, but we migth had one in the past.
                a_attributes_to_clean.push('silva_reference');
                a_attributes_to_clean.push('silva_target');
                a_attributes_to_clean.push('silva_anchor');
                a_attributes_to_clean.push('target');
                a_attributes_to_clean.push('title');
            };
            a.setAttributes(a_attributes);
            if (a_attributes_to_clean.length) {
                a.removeAttributes(a_attributes_to_clean);
            };
            // Image tag
            if (a.getChildCount()) {
                img = a.getChild(0);
                if (!img.is('img')) {
                    img = null;
                };
                if (img == null) {
                    // Clean all following tags, they are faulty.
                    for (var i=0; i < a.getChildCount();) {
                        a.getChild(0).remove();
                    };
                };
            };
            if (img == null) {
                img = new CKEDITOR.dom.element('img');
                a.append(img);
            };
            if (data.image.alt) {
                img_attributes['alt'] = data.image.alt;
            } else {
                img_attributes_to_clean.push('alt');
            };
            if (data.image.type == 'intern') {
                img_attributes['silva_reference'] = 'new';
                img_attributes['silva_target'] = data.image.content;
            } else {
                img_attributes_to_clean.push('silva_reference');
                img_attributes_to_clean.push('silva_target');
            };
            img.setAttributes(img_attributes);
            if (img_attributes_to_clean.length) {
                img.removeAttributes(img_attributes_to_clean);
            };
            // Span tag: caption
            if (a.getChildCount() == 2) {
                caption = a.getChild(1);
                if (!caption.is('span') || !caption.hasClass('caption')) {
                    caption = null;
                };
                if (caption == null) {
                    // Clean all following tags, they are faulty.
                    for (var i=1; i < a.getChildCount();) {
                        a.getChild(1).remove();
                    };
                };
            };
            if (data.image.caption) {
                if (caption == null) {
                    var caption_attributes = {};

                    caption = new CKEDITOR.dom.element('span');
                    caption_attributes['class'] = 'caption';
                    caption.setAttributes(caption_attributes);
                    a.append(caption);
                };
                caption.setText(data.image.caption);
            } else if (caption != null) {
                // There was a caption, we need to remove it.
                caption.remove();
            };
        }
    };
});
