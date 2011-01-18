
(function(CKEDITOR){

    CKEDITOR.plugins.silvaimage = {
        isImage: function(element) {
            if (element != null &&
                element.is('div') &&
                element.hasClass('image')) {
                return true;
            };
            return false;
        },
        getSelectedImage: function(editor, select_base_element) {
            try {
                var selection = editor.getSelection();
                var base = null;

                if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                    base = selection.getSelectedElement();
                } else {
                    base = selection.getStartElement();
                };

                var element = base.getAscendant('div', true);

                if (CKEDITOR.plugins.silvaimage.isImage(element)) {
                    if (base.$ !== element.$ && select_base_element) {
                        selection.selectElement(element);
                    }
                    return element;
                };
                return null;
            }
            catch(e) {
                return null;
            }
        }
    };

    var API = CKEDITOR.plugins.silvaimage;

    CKEDITOR.plugins.add('silvaimage', {
        requires: ['dialog', 'silvareference', 'silvalink'],
        init: function(editor) {
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
                    'padding: 1px;' +
                    'color: #444;' +
                    'background-color: #EEE8AA;' +
                    'display: inline-block;' +
                    '}');
            editor.addCss(
                'div.image span.image-caption {' +
                    'display: block;' +
                    'padding-left: 5px' +
                    '}');
            editor.addCss(
                'div.float-left {' +
                    'float: left;' +
                    '}');
            editor.addCss(
                'div.float-right {' +
                    'float: right;' +
                    '}');
            editor.addCss(
                'div.image-left {' +
                    'text-align: left;' +
                    'display: block;' +
                    '}');
            editor.addCss(
                'div.image-right {' +
                    'text-align: right;' +
                    'display: block;' +
                    '}');
            editor.addCss(
                'div.image-center {' +
                    'text-align: center;' +
                    'display: block;' +
                    '}');
            // Events
            editor.on('selectionChange', function(event) {
                var element = API.getSelectedImage(editor, true);
                var imageCommand = editor.getCommand('silvaimage');

                if (element != null) {
                    imageCommand.setState(CKEDITOR.TRISTATE_ON);
                } else {
                    imageCommand.setState(CKEDITOR.TRISTATE_OFF);
                };
            });
            editor.on('doubleclick', function(event){
                var element = API.getSelectedImage(editor, true);

                if (element != null) {
                    event.data.dialog = 'silvaimage';
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
            // Input / Output transformations
            var dataProcessor = editor.dataProcessor;
            var dataFilter = dataProcessor && dataProcessor.dataFilter;
            var htmlFilter = dataProcessor && dataProcessor.htmlFilter;

            var remove = function(attributes, name) {
                // Remove an attribute from an object.
                if (attributes[name]) {
                    delete attributes[name];
                };
            };
            var is_img_div = function(element) {
                // Test if the given element is an image div.
                return (element &&
                        element.name == 'div' &&
                        element.attributes['class'] != undefined &&
                        element.attributes['class'].match('image'));
            };
            var is_img_a = function(element) {
                // Test if the given element is image link.
                return (element &&
                        element.name == 'a' &&
                        element.attributes['class'] == 'image-link');
            };

            if (dataFilter) {
                dataFilter.addRules({
                    elements: {
                        div: function(element) {
                            var attributes = element.attributes;

                            if (is_img_div(element)) {
                                attributes['contenteditable'] = 'false';
                            } else {
                                remove(attributes, 'style');
                            };
                            return null;
                        },
                        img: function(element) {
                            var parent = element.parent;
                            var attributes = element.attributes;

                            if (!is_img_div(parent) && !is_img_a(parent)) {
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
                                if (!attributes['_silva_src']) {
                                    attributes['_silva_src'] =
                                        attributes['src'] ||
                                        attributes['data-cke-saved-src'];
                                };
                                return div;
                            };
                            return null;
                        }
                    }
                });
            };
            if (htmlFilter) {
                htmlFilter.addRules({
                    elements: {
                        div: function(element) {
                            if (is_img_div(element)) {
                                var attributes = element.attributes;

                                remove(attributes, 'contenteditable');
                                remove(attributes, 'style');
                            };
                        }
                    }
                });
            };
        }
    });
})(CKEDITOR);
