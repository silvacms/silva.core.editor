

(function(CKEDITOR, $){
    /**
     * CKEditor Plugin for Images in Silva. They are represented in
     * the editor like this:
     *
     * <span class="inline-container image-container alignement">
     *    <div class="image">
     *       <a class="image-link" href="">
     *          <img alt="Alt text" />
     *       </a>
     *       <span class="image-caption">Caption</span>
     *    </div>
     * </span>
     */

    CKEDITOR.plugins.silvaimage = {
        isImageWrapper: function(element) {
            // Return true if the element is an image wrapper.
            if (element != null &&
                element.type == CKEDITOR.NODE_ELEMENT &&
                element.is('span') &&
                element.hasClass('image-container')) {
                return true;
            }
            return false;
        },
        isImage: function(element) {
            // Given an element return true if it is an image.
            if (element != null &&
                element.is('div') &&
                element.hasClass('image')) {
                return true;
            };
            return false;
        },
        findImage: function(element) {
            // Given an element find the nearest image.
            var image;

            if (element !== null) {
                image = element.getAscendant('span', true);
                if (API.isImageWrapper(image)) {
                    var children = image.getChildren(),
                        i, len, child;
                    for (i=0, len=children.count(); i < len; i++) {
                        child = children.getItem(i);
                        if (API.isImage(child)) {
                            return child;
                        };
                    };
                };

                image = element.getAscendant('div', true);
                if (API.isImage(image)) {
                    return image;
                };
            };
            return null;

        },
        setCurrentImage: function(editor, image) {
            // Save the currently edited image in the editor. This is
            // used to pass the image to the command.
            editor._.silvaWorkingImage = image;
        },
        getCurrentImage: function(editor) {
            // Return the image that is currently being modified. This
            // is used instead of getSelectedImage because the editor
            // selection can change during the modification, and the
            // reference to the image lost.
            if (editor._.silvaWorkingImage  !== undefined) {
                return editor._.silvaWorkingImage;
            };
            return null;
        },
        getSelectedImage: function(editor, no_selection) {
            // Find the currently selected image. Correct the selection if needed.
            var selected = CKEDITOR.silva.utils.getSelectedElement(editor),
                image = API.findImage(selected),
                wrapper = null;

            if (image !== null) {
                if (!no_selection) {
                    wrapper = image.getParent();
                    if (!API.isImageWrapper(wrapper)) {
                        wrapper = image;
                    };
                    // Select the wrapper if needed.
                    if (selected.$ !== wrapper.$) {
                        CKEDITOR.silva.utils.selectBlock(editor, wrapper);
                    };
                };
                return image;
            };
            return null;
        }
    };


    var API = CKEDITOR.plugins.silvaimage;

    CKEDITOR.plugins.add('silvaimage', {
        requires: ['dialog', 'silvautils', 'silvalink'],
        init: function(editor) {
            var UTILS = CKEDITOR.silva.utils;

            editor.addCommand(
                'silvaimage',
                new CKEDITOR.dialogCommand('silvaimage'));
            editor.ui.addButton('SilvaImage', {
                label : 'Image properties',
                command : 'silvaimage',
                className: 'cke_button_image'
            });
            editor.addCss(
                'div.image {' +
                    'z-index: 1;' +
                    'padding: 1px;' +
                    'color: #444;' +
                    'display: inline-block;' +
                    '}');
            editor.addCss(
                'div.image img {' +
                    'z-index: -1;' +
                    '}');
            editor.addCss(
                'div.image span.image-caption {' +
                    'display: block;' +
                    'padding-left: 5px' +
                    '}');

            // Events
            editor.on('selectionChange', function(event) {
                var image = API.getSelectedImage(editor),
                    command = editor.getCommand('silvaimage');

                API.setCurrentImage(editor, image);
                if (image != null) {
                    command.setState(CKEDITOR.TRISTATE_ON);
                } else {
                    command.setState(CKEDITOR.TRISTATE_OFF);
                };
            });
            editor.on('doubleclick', function(event) {
                var image = API.getSelectedImage(editor);

                API.setCurrentImage(editor, image);
                if (image != null) {
                    event.data.dialog = 'silvaimage';
                };
            });
            if (!CKEDITOR.env.gecko) {
                editor.on('contentDom', function() {
                    editor.document.on('mousedown', function(event) {
                        var selected,
                            image = API.findImage(event.data.getTarget()),
                            wrapper;

                        if (image !== null) {
                            wrapper = image.getParent();
                            if (!API.isImageWrapper(wrapper)) {
                                wrapper = image;
                            };
                            selected = UTILS.getSelectedElement(editor);
                            if (selected === null || selected.$ !== wrapper.$) {
                                UTILS.selectBlock(editor, wrapper);
                            };
                            // Prevent broken drag'n drop.
                            event.data.preventDefault();
                        };
                    });
                });
                };
            editor.on('key', function(event) {
                // Improve the navigation before and after the image with the arrows.
                if (editor.mode != 'wysiwyg')
                    return;

                var code = event.data.keyCode;
                if (code in {9:1, 37:1, 38:1, 39:1, 40:1}) {
                    setTimeout(function() {
                        var image = API.getSelectedImage(editor, true),
                            parent = null,
                            on_top = code in {37:1, 38:1};

                        if (image !== null) {
                            parent = image.getParent();
                            if (!API.isImageWrapper(parent)) {
                                parent = image;
                            };
                            UTILS.selectText(editor, UTILS.getParagraph(editor, parent, on_top), on_top);
                        };
                    }, 0);
                };
            });

            // Dialog
            CKEDITOR.dialog.add('silvaimage', this.path + 'dialogs/image.js');
            // Menu
            if (editor.addMenuItems) {
                editor.addMenuItems({
                    image: {
                        label: editor.lang.image.menu,
                        command : 'silvaimage',
                        group : 'image',
                        order: 1
                    }
                });
            };
            if (editor.contextMenu) {
                editor.contextMenu.addListener(function(element, selection) {
                    if (API.isImage(element.getAscendant('div', true))) {
                        return  {
                            image: CKEDITOR.TRISTATE_OFF
                        };
                    };
                    return null;
                });
            };
        },
        afterInit: function(editor) {

            var remove = function(attributes, name) {
                // Remove an attribute from an object.
                if (attributes[name]) {
                    delete attributes[name];
                };
            };
            var is_container = function(element) {
                // Test if the given element is an image div.
                return (element &&
                        element.name == 'div' &&
                        element.attributes['class'] != undefined &&
                        element.attributes['class'].match('image'));
            };
            var is_link = function(element) {
                // Test if the given element is image link.
                return (element &&
                        element.name == 'a' &&
                        element.attributes['class'] == 'image-link');
            };

            // Input / Output transformations
            var dataProcessor = editor.dataProcessor,
                dataFilter = dataProcessor && dataProcessor.dataFilter,
                htmlFilter = dataProcessor && dataProcessor.htmlFilter,
                WRAPPER = new CKEDITOR.silva.parser.Wrapper(is_container, 'image-container'),
                ALIGNEMENT = new CKEDITOR.silva.RE(/^image (.*)$/, 'default');


            if (dataFilter) {
                dataFilter.addRules({
                    elements: {
                        div: function(element) {
                            if (is_container(element)) {
                                element.attributes['contenteditable'] = 'false';
                                return WRAPPER.wrap(
                                    element,
                                    ALIGNEMENT.extract(element.attributes['class']));
                            } else {
                                remove(element.attributes, 'style');
                            };
                            return null;
                        },
                        img: function(element) {
                            var parent = element.parent,
                                attributes = element.attributes;

                            if (!is_container(parent) && !is_link(parent)) {
                                // This is an image from the outside world.
                                // Prepare a structure.
                                var div = new CKEDITOR.htmlParser.fragment.fromHtml(
                                    '<div class="image default"></div>').children[0];

                                // Insert the div before the image.
                                div.children = [element];
                                div.parent = element.parent;
                                element.parent = div;

                                // Clean attributes
                                remove(attributes, 'style');
                                remove(attributes, 'height');
                                remove(attributes, 'width');
                                // Save the src tag
                                if (!attributes['data-silva-url'] &&
                                    !attributes['data-silva-reference']) {
                                    attributes['data-silva-url'] =
                                        attributes['data-cke-saved-src'] ||
                                        attributes['src'];
                                };
                                return WRAPPER.wrap(div, 'default');
                            };
                            if (!attributes['src']){
                                var src = attributes['data-silva-url'] || attributes['data-silva-backup'];
                                if (src) {
                                    attributes['src'] = src;
                                    attributes['data-cke-saved-src'] = src;
                                };
                            } else if (attributes['data-silva-reference']) {
                                // Backup URL is used by reference to keep URL between
                                // source and edit mode.
                                attributes['data-silva-backup'] = attributes['src'];
                            };
                            return null;
                        }
                    }
                });
            };
            if (htmlFilter) {
                htmlFilter.addRules({
                    elements: {
                        span: function(element) {
                            return WRAPPER.remove(element);
                        },
                        div: function(element) {
                            if (is_container(element)) {
                                remove(element.attributes, 'contenteditable');
                                remove(element.attributes, 'style');
                            };
                            return null;
                        },
                        a: function(element) {
                            var attributes = element.attributes;

                            if (attributes['class'] == 'image-link') {
                                remove(attributes, 'data-cke-saved-href');
                                remove(attributes, 'href');
                            };
                            return null;
                        },
                        img: function(element) {
                            var attributes = element.attributes;

                            remove(attributes, 'data-cke-saved-src');
                            remove(attributes, 'src');
                            return null;
                        }
                    }
                });
            };
        }
    });
})(CKEDITOR, jQuery);
