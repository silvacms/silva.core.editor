

CKEDITOR.dialog.add('silvaimage', function(editor) {

    return {
        title: 'Image properties',
        minWidth: 350,
        minHeight: 230,
        contents: [{
            id: 'image',
            label: 'Image',
            elements: [{
                type: 'radio',
                id: 'image_type',
                label: 'Image type',
                items: [
                    ['internal image', 'intern'],
                    ['external image', 'extern']
                ],
                'default': 'intern',
                required: true,
                onChange: function() {
                    var value = this.getValue();
                    var dialog = this.getDialog();
                    var url_input = dialog.getContentElement(
                        'image', 'image_url').getElement();
                    var reference_input = dialog.getContentElement(
                        'image', 'image_content').getElement();

                    switch (value) {
                    case 'intern':
                        url_input.hide();
                        reference_input.show();
                        break;
                    case 'extern':
                        reference_input.hide();
                        url_input.show();
                        break;
                    }
                },
                setup: function(data) {
                    this.setValue(data.image.type);
                },
                commit: function(data) {
                    data.image.type = this.getValue();
                }
            }, {
                type: 'text',
                id: 'image_url',
                label: 'Image URL',
                required: true,
                setup: function(data) {
                    this.setValue(data.image.url);
                },
                validate: function() {
                    var dialog = this.getDialog();
                    var type_value = dialog.getContentElement('image', 'image_type').getValue();

                    if (type_value == 'extern') {
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
            }, {
                type: 'reference',
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
                        var value = this.getValue();

                        if (!value || value == '0') {
                            return 'You need to select an image to insert !';
                        };
                    };
                    return true;
                },
                commit: function(data) {
                    data.image.content = this.getValue();
                }
            },{
                type: 'select',
                id: 'image_align',
                label: 'Image alignement',
                required: true,
                items: [
                    ['default', 'default'],
                    ['align left', 'align-left'],
                    ['align center', 'align-center'],
                    ['align right', 'align-right'],
                    ['float left', 'float-left'],
                    ['float right', 'float-right']
                ],
                setup: function(data) {
                    this.setValue(data.image.align);
                },
                commit: function(data) {
                    data.image.align = this.getValue();
                }
            }, {
                type: 'text',
                id: 'image_alt',
                label: 'Image alternative text',
                required: false,
                setup: function(data) {
                    this.setValue(data.image.alt);
                },
                commit: function(data) {
                    data.image.alt = this.getValue();
                }
            }, {
                type: 'text',
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
            }, {
                type: 'checkbox',
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
        }, {
            id: 'link',
            label: 'Link',
            elements: [{
                type: 'checkbox',
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
                    var dialog = this.getDialog();

                    if (this.getValue()) {
                        var image = dialog.getContentElement(
                            'image', 'image_content');

                        data.link.type = 'intern';
                        data.link.content = image.getValue();
                    } else {
                        var custom = dialog.getContentElement(
                            'link', 'link_custom');

                        if (!custom.getValue()) {
                            // None of the two check box are checked.
                            // Set link type to none to prevent
                            // link fields to be used.
                            data.link.type = null;
                        };
                    };
                }
            }, {
                type: 'checkbox',
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
            }, {
                type: 'vbox',
                id: 'link_options',
                children: CKEDITOR.plugins.silvalink.createDialogFields(function (validator) {
                    return function () {
                        var dialog = this.getDialog();
                        var activated = dialog.getContentElement(
                            'link', 'link_custom').getValue();

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

            var defaultSettings = function() {
                data.link = {};
                data.image = {};
                data.image.type = 'intern';
                data.link.type = null;
                data.link.target = '_self';
            };
            defaultSettings();

            var parseError = function(msg, element) {
                if (window.console && console.log) {
                    console.log(msg + ": " + element.getOuterHtml());
                };
                defaultSettings();
            };

            var parseImage = function(img) {
                if (img.is('img')) {
                    data.image.alt = img.$.getAttribute('alt');
                    data.image.url = img.$.getAttribute('src');
                    if (img.$.hasAttribute('data-silva-reference')) {
                        data.image.type = 'intern';
                        data.image.content = img.$.getAttribute('data-silva-target');
                    } else {
                        data.image.type = 'extern';
                        data.image.url = img.$.getAttribute('data-silva-url');
                    };
                    if (img.hasNext()) {
                        var caption = img.getNext();

                        while(caption.is('br') && caption.hasNext())
                            caption = caption.getNext();

                        if (!caption.is('br')) {
                            if (caption.is('span') &&
                                caption.hasClass('image-caption')) {
                                data.image.caption = caption.getText();
                            } else {
                                parseError("Invalid image caption", caption);
                            };
                        };
                    };
                } else {
                    parseError("Invalid image tag", img);
                };
            };

            if (div != null) {
                var parse_alignment = /^image\s+([a-z-]+)\s*$/;
                var info_alignment = parse_alignment.exec(
                    div.getAttribute('class'));

                if (info_alignment != null) {
                    data.image.align = info_alignment[1];
                }
                if (div.getChildCount()) {
                    var a = div.getChild(0);

                    if (a.is('a')) {
                        data.link.title = a.getAttribute('title');
                        data.link.target = a.getAttribute('target');
                        data.link.anchor = a.getAttribute('data-silva-anchor');
                        if (a.$.hasAttribute('data-silva-reference')) {
                            data.link.type = 'intern';
                            data.link.content = a.getAttribute('data-silva-target');
                        } else {
                            var href = a.getAttribute('data-silva-url');

                            if (!href || href == 'javascript:void()') {
                                data.link.type = 'anchor';
                            } else {
                                data.link.type = 'extern';
                                data.link.url = href;
                            };
                        };

                        if (a.getChildCount()) {
                            parseImage(a.getChild(0));
                        };
                    } else {
                        parseImage(a);
                    };
                } else {
                    parseError("Invalid image structure", div);
                };
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
            var img = null;
            var img_attributes = {src: data.image.url};
            var img_attributes_to_clean = [];
            var caption = null;

            // Div tag: image container
            div_attributes['class'] = 'image ' + data.image.align;
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
                var start = 0;

                if (div.getChildCount()) {
                    a = div.getChild(0);
                    if (a.is('a')) {
                        start += 1;
                    } else {
                        if (a.is('img')) {
                            img = a;
                            start += 1;
                            if (a.hasNext()) {
                                caption = a.getNext();
                                if (caption.is('span') &&
                                    caption.hasClass('image-caption')) {
                                    start += 1;
                                } else {
                                    caption = null;
                                };
                            };
                        };
                        a = null;
                    };
                };
                // Ok, we have what we went, clean all other nodes.
                for (; start < div.getChildCount();) {
                    div.getChild(start).remove();
                };
            };
            div.setAttributes(div_attributes);
            // Link tag
            if (a != null && a.getChildCount()) {
                var start = 0;

                img = a.getChild(0);
                if (img.is('img')) {
                    start += 1;
                    if (img.hasNext()) {
                        caption = img.getNext();
                        if (caption.is('span') &&
                            caption.hasClass('image-caption')) {
                            start += 1;
                        } else {
                            caption = null;
                        };
                    }
                } else {
                    img = null;
                }
                // Clean all following tags, they are faulty.
                for (; start < a.getChildCount();) {
                    a.getChild(start).remove();
                };
            };
            if (data.link.type) {
                var attributes = {};
                var attributes_to_clean = [];

                if (a == null) {
                    a = new CKEDITOR.dom.element('a');
                    attributes['href'] = 'javascript:void()';
                    attributes['class'] = 'image-link';
                    div.append(a);
                    if (img) {
                        img.move(a);
                    };
                    if (caption) {
                        caption.move(a);
                    };
                };

                var update_attribute = function(key, value) {
                    if (value) {
                        attributes[key] = value;
                    } else {
                        attributes_to_clean.push(key);
                    }
                };

                update_attribute('target', data.link.target);
                update_attribute('title', data.link.title);
                update_attribute('data-silva-anchor', data.link.anchor);

                switch (data.link.type) {
                case 'intern':
                    attributes['data-silva-reference'] = 'new';
                    attributes['data-silva-target'] = data.link.content;
                    attributes_to_clean.push('data-silva-url');
                    break;
                case 'extern':
                    attributes['href'] = 'javascript:void()';
                    attributes['data-silva-url'] = data.link.url;
                    attributes_to_clean.push('data-silva-reference');
                    attributes_to_clean.push('data-silva-target');
                    break;
                case 'anchor':
                    attributes_to_clean.push('data-silva-reference');
                    attributes_to_clean.push('data-silva-target');
                    attributes_to_clean.push('data-silva-url');
                    break;
                };
                a.setAttributes(attributes);
                if (attributes_to_clean.length) {
                    a.removeAttributes(attributes_to_clean);
                };
            } else {
                if (a) {
                    a.remove(true);
                    a = null;
                };
            };
            // Image tag
            if (img == null) {
                img = new CKEDITOR.dom.element('img');
                if (a) {
                    a.append(img);
                } else {
                    div.append(img);
                };
            };
            if (data.image.alt) {
                img_attributes['alt'] = data.image.alt;
            } else {
                img_attributes_to_clean.push('alt');
            };
            if (data.image.type == 'intern') {
                img_attributes['data-silva-reference'] = 'new';
                img_attributes['data-silva-target'] = data.image.content;
                img_attributes['data-silva-backup'] = data.image.url;
                img_attributes_to_clean.push('data-silva-url');
            } else {
                img_attributes['data-silva-url'] = data.image.url;
                img_attributes_to_clean.push('data-silva-reference');
                img_attributes_to_clean.push('data-silva-target');
                img_attributes_to_clean.push('data-silva-backup');
            };
            img.setAttributes(img_attributes);
            if (img_attributes_to_clean.length) {
                img.removeAttributes(img_attributes_to_clean);
            };
            // Span tag: caption
            if (data.image.caption) {
                if (caption == null) {
                    var attributes = {};

                    caption = new CKEDITOR.dom.element('span');
                    attributes['class'] = 'image-caption';
                    caption.setAttributes(attributes);
                    if (a) {
                        a.append(caption);
                    } else {
                        div.append(caption);
                    }
                };
                caption.setText(data.image.caption);
            } else if (caption != null) {
                // There was a caption, we need to remove it.
                caption.remove();
            };
        }
    };
});
