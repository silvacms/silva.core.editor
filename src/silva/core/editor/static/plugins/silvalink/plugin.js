


(function(CKEDITOR){

    CKEDITOR.unlinkCommand = function(){};
    CKEDITOR.unlinkCommand.prototype = {
        exec: function(editor) {
            // This is taken from the official link plugins. Should use
            // the styling system to change this. Firefox let a span when
            // a link is removed.
            var selection = editor.getSelection();
            var bookmarks = selection.createBookmarks();
            var ranges = selection.getRanges();
            var rangeRoot;
            var element;

            for (var i=0 ; i < ranges.length ; i++) {
                rangeRoot = ranges[i].getCommonAncestor(true);
                element = rangeRoot.getAscendant('a', true);
                if (!element)
                    continue;
                ranges[i].selectNodeContents(element);
            }

            selection.selectRanges(ranges);
            editor.document.$.execCommand('unlink', false, null);
            selection.selectBookmarks(bookmarks);
        },
        startDisabled: true
    };

    CKEDITOR.plugins.silvalink = {
        isLink: function(element) {
            if (element != null && element.is('a') && element.hasClass('link')) {
                return true;
            };
            return false;
        },
        getSelectedLink: function(editor) {
            try {
                var selection = editor.getSelection(),
                    selected;

                if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                    selected = selection.getSelectedElement();
                    if (CKEDITOR.plugins.silvalink.isLink(selected)) {
                        return selected;
                    };
                };

                var ranges = selection.getRanges(true)[0];
                if (ranges != undefined) {
                    ranges.shrink(CKEDITOR.SHRINK_TEXT);

                    var base = ranges.getCommonAncestor();
                    selected = base.getAscendant('a', true);
                    if (CKEDITOR.plugins.silvalink.isLink(selected)) {
                        return selected;
                    };
                };
                return null;
            } catch(e) {
                return null;
            };
        },
        insertAndSelectTextIfNoneSelected: function(editor, text) {
            var selection = editor.getSelection(),
                ranges = selection.getRanges(true);

            if (ranges.length == 1 && ranges[0].collapsed) {
                var node = new CKEDITOR.dom.text(text);

                ranges[0].insertNode(node);
                ranges[0].selectNodeContents(node);
                selection.selectRanges(ranges);
            }
        },
        createDialogFields: function (validatorDecorator) {
            // validatorDecorator is used to decorate validation functions.
            if (validatorDecorator == null) {
                // No decorator, create a default one.
                validatorDecorator = function(validator) {
                    return validator;
                };
            };
            // Define popup fields for links. They are defined here to be
            // used in other plugins.
            return [
                { type: 'radio',
                  id: 'link_type',
                  label: 'Link type',
                  items: [
                      ['internal link', 'intern'],
                      ['external link', 'extern'],
                      ['local anchor', 'anchor']
                  ],
                  required: true,
                  updateStatus: function () {
                      var value = this.getValue();
                      var dialog = this.getDialog();
                      var url_input = dialog.getContentElement(
                          'link', 'link_url').getElement();
                      var reference_input = dialog.getContentElement(
                          'link', 'link_content').getElement();
                      var anchor_input = dialog.getContentElement(
                          'link', 'link_anchor').getElement();
                      var extra_anchor_input = dialog.getContentElement(
                          'link', 'link_extra_anchor').getElement();

                      switch(value) {
                      case 'intern':
                          url_input.hide();
                          anchor_input.hide();
                          reference_input.show();
                          extra_anchor_input.show();
                          break;
                      case 'extern':
                          reference_input.hide();
                          anchor_input.hide();
                          url_input.show();
                          extra_anchor_input.show();
                          break;
                      default:
                          url_input.hide();
                          reference_input.hide();
                          extra_anchor_input.hide();
                          anchor_input.show();
                      };
                  },
                  onChange: function() {
                      this.updateStatus();
                  },
                  onClick: function() {
                      // IE doesn't trigger change when the radio is switched.
                      if (CKEDITOR.env.ie) {
                          this.updateStatus();
                      }
                  },
                  setup: function(data) {
                      this.setValue(data.link.type);
                  },
                  commit: function(data) {
                      if (data.link.type === undefined) {
                          data.link.type = this.getValue();
                      };
                  }
                },
                { type: 'text',
                  id: 'link_url',
                  label: 'External URL',
                  required: true,
                  setup: function(data) {
                      this.setValue(data.link.url);
                  },
                  validate: validatorDecorator(function() {
                      var dialog = this.getDialog();
                      var type_value = dialog.getContentElement(
                          'link', 'link_type').getValue();

                      if (type_value == 'extern') {
                          var checker = CKEDITOR.dialog.validate.regex(
                                  /^(?:http|https|ftp|ftps|ssh|news|mailto|tel|webcal|itms):.*$/,
                              'You need to specify a valid external URL !');

                          return checker.apply(this);
                      };
                      return true;
                  }),
                  commit: function(data) {
                      if (data.link.url === undefined) {
                          data.link.url = this.getValue();
                      };
                  }
                },
                { type: 'reference',
                  id: 'link_content',
                  label: 'Link target',
                  required: true,
                  onReferenceUpdate: function(event) {
                      var dialog = this.getDialog();
                      var title = dialog.getContentElement('link', 'link_title');

                      if (!title.getValue()) {
                          title.setValue(event.data.title);
                      };
                  },
                  validate: validatorDecorator(function() {
                      var dialog = this.getDialog();
                      var type_value = dialog.getContentElement('link', 'link_type').getValue();

                      if (type_value == 'intern') {
                          var value = this.getValue();

                          if(!value || value == '0') {
                              return  'You need to select a item to link to !';
                          };
                      };
                      return true;
                  }),
                  setup: function(data) {
                      if (data.link.content !== undefined) {
                          this.setValue(data.link.content);
                      } else {
                          this.clear();
                      };
                  },
                  commit: function(data) {
                      if (data.link.content === undefined) {
                          data.link.content = this.getValue();
                      };
                  }
                },
                { type: 'select',
                  id: 'link_anchor',
                  label: 'Anchor',
                  items: [],
                  required: true,
                  setup: function(data) {
                      var editor = this.getDialog().getParentEditor();
                      var anchors = CKEDITOR.plugins.silvaanchor.listDocumentAnchors(
                          editor);

                      this.clear();
                      this.add('No anchor selected', '');
                      for (var i=0; i < anchors.length; i++ ) {
                          this.add(anchors[i][1], anchors[i][0]);
                      };
                      if (data.link.type == 'anchor') {
                          this.setValue(data.link.anchor);
                      };
                  },
                  validate: validatorDecorator(function() {
                      var dialog = this.getDialog();
                      var type_value = dialog.getContentElement(
                          'link', 'link_type').getValue();

                      if (type_value == 'anchor') {
                          var checker = CKEDITOR.dialog.validate.notEmpty(
                              'You need to select a document anchor !');

                          return checker.apply(this);
                      };
                      return true;
                  }),
                  commit: function(data) {
                      var dialog = this.getDialog();
                      var type_value = dialog.getContentElement(
                          'link', 'link_type').getValue();

                      if (type_value == 'anchor') {
                          data.link.anchor = this.getValue();
                      };
                  }
                },
                { type: 'text',
                  id: 'link_extra_anchor',
                  label: 'Anchor',
                  setup: function(data) {
                      this.setValue(data.link.anchor);
                  },
                  commit: function(data) {
                      var dialog = this.getDialog();
                      var type_value = dialog.getContentElement(
                          'link', 'link_type').getValue();

                      if (type_value != 'anchor') {
                          data.link.anchor = this.getValue();
                      };
                  }
                },
                { type: 'select',
                  id: 'link_target',
                  label: 'Window target',
                  items: [
                      ['same window', '_self'],
                      ['new window', '_blank'],
                      ['parent', '_parent'],
                      ['top', '_top'],
                      ['custom target', 'input']
                  ],
                  required: true,
                  onChange: function() {
                      // IE triggers change when the select is changed !
                      var dialog = this.getDialog();
                      var target_value = dialog.getContentElement(
                          'link', 'link_target').getValue();
                      var input = dialog.getContentElement(
                          'link', 'link_custom_target');

                      if (target_value == 'input') {
                          input.getElement().show();
                      } else {
                          input.getElement().hide();
                      };
                  },
                  setup: function(data) {
                      var is_custom = true;
                      var items = this._.select.items;

                      for (var i = 0; i < items.length; i++) {
                          if (items[i][1] == data.link.target) {
                              is_custom = false;
                              break;
                          };
                      };
                      if (is_custom) {
                          var dialog = this.getDialog();
                          var custom_target = dialog.getContentElement(
                              'link', 'link_custom_target');

                          custom_target.setValue(data.link.target);
                          this.setValue('input');
                      } else {
                          this.setValue(data.link.target);
                      }
                  },
                  commit: function(data) {
                      var target = this.getValue();

                      if (target == 'input') {
                          var dialog = this.getDialog();
                          var custom_target = dialog.getContentElement(
                              'link', 'link_custom_target');

                          target = custom_target.getValue();
                      };
                      data.link.target = target;
                  }
                },
                { type: 'text',
                  id: 'link_custom_target',
                  label: 'Custom target',
                  required: true,
                  validate: validatorDecorator(function() {
                      var dialog = this.getDialog();
                      var target_value = dialog.getContentElement(
                          'link', 'link_target').getValue();

                      if (target_value == 'input') {
                          var checker = CKEDITOR.dialog.validate.notEmpty(
                              'Custom window target is selected for the link, ' +
                                  'but no custom target is filled !');

                          return checker.apply(this);
                      };
                      return true;
                  })
                  // Setup and commit are done by the target field.
                },
                { type: 'text',
                  id: 'link_title',
                  label: 'Link title',
                  setup: function(data) {
                      this.setValue(data.link.title);
                  },
                  commit: function(data) {
                      data.link.title = this.getValue();
                  }
                }
            ];
        }
    };

    var API = CKEDITOR.plugins.silvalink;

    CKEDITOR.plugins.add('silvalink', {
        requires: ['dialog', 'silvautils'],
        init: function(editor) {
            editor.addCommand(
                'silvalink',
                new CKEDITOR.dialogCommand('silvalink'));
            editor.addCommand(
                'silvaunlink',
                new CKEDITOR.unlinkCommand());
            editor.ui.addButton('SilvaLink', {
                label: 'Link properties',
                command: 'silvalink',
                className: 'cke_button_link'
            });
            editor.ui.addButton('SilvaUnlink', {
                label: 'Remove link',
                command: 'silvaunlink',
                className: 'cke_button_unlink'
            });
            // Event
            editor.on('selectionChange', function(event) {
                var element = API.getSelectedLink(editor);
                var linkCommand = editor.getCommand('silvalink');
                var unlinkCommand = editor.getCommand('silvaunlink');

                if (element != null) {
                    linkCommand.setState(CKEDITOR.TRISTATE_ON);
                    unlinkCommand.setState(CKEDITOR.TRISTATE_OFF);
                } else {
                    linkCommand.setState(CKEDITOR.TRISTATE_OFF);
                    unlinkCommand.setState(CKEDITOR.TRISTATE_DISABLED);
                };
            });
            editor.on('doubleclick', function(event) {
                var element = API.getSelectedLink(editor);

                if (element != null) {
                    event.data.dialog = 'silvalink';
                };
            });
            // Dialog
            CKEDITOR.dialog.add('silvalink', this.path + 'dialogs/link.js');
            // Menu
            if (editor.addMenuItems) {
                editor.addMenuItems({
                    link: {
                        label: editor.lang.link.menu,
                        command : 'silvalink',
                        group : 'link',
                        order: 10
                    },
                    unlink: {
                        label: editor.lang.unlink,
                        command: 'silvaunlink',
                        group: 'link',
                        order: 15
                    }
                });
            };
            if (editor.contextMenu) {
                editor.contextMenu.addListener(function(element, selection) {
                    if (API.isLink(element)) {
                        return  {
                            link: CKEDITOR.TRISTATE_OFF,
                            unlink: CKEDITOR.TRISTATE_OFF
                        };
                    };
                    return null;
                });
            };
        },
        afterInit: function(editor) {
            // Register a filter to displaying placeholders after mode change.

            var dataProcessor = editor.dataProcessor;
            var dataFilter = dataProcessor && dataProcessor.dataFilter;
            var htmlFilter = dataProcessor && dataProcessor.htmlFilter;

            var remove = function(attributes, name) {
                if (attributes[name]) {
                    delete attributes[name];
                };
            };

            if (dataFilter) {
                dataFilter.addRules({
                    elements: {
                        a: function(element) {
                            var attributes = element.attributes;

                            if (!attributes['class']) {
                                if (attributes['name'] && attributes['href']) {
                                    attributes['class'] = 'anchor';
                                } else {
                                    attributes['class'] = 'link';
                                };
                            };
                            if (attributes['class'] == 'link') {
                                if (!attributes['data-silva-url'] &&
                                    !attributes['data-silva-reference'] &&
                                    !attributes['data-silva-anchor']) {
                                    // Backup the href attribute into
                                    // data-silva-url: href get removed in
                                    // case of copy and paste in some obscur cases.
                                    attributes['data-silva-url'] =
                                        attributes['data-cke-saved-href'] ||
                                        attributes['href'];
                                };
                                if (!attributes['href']) {
                                    // Ensure we have a disabled link;
                                    attributes['href'] = 'javascript:void(0)';
                                };
                            };
                            return null;
                        }
                    }
                });
            };
            if (htmlFilter) {
                htmlFilter.addRules({
                    elements: {
                        a: function(element) {
                            var attributes = element.attributes;

                            if (attributes['class'] == 'link') {
                                remove(attributes, 'data-cke-saved-href');
                                remove(attributes, 'href');
                            };
                            return null;
                        }
                    }
                });
            };
        }
    });
})(CKEDITOR);
