
CKEDITOR.plugins.add('silvalink', {
    requires: ['dialog', 'silvareference'],
    init: function(editor) {
        editor.addCommand('silvalink', new CKEDITOR.dialogCommand('silvalink'));
        editor.addCommand('silvaunlink', new CKEDITOR.unlinkCommand());
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
            var element = CKEDITOR.plugins.silvalink.getSelectedLink(editor);
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
            var element = CKEDITOR.plugins.silvalink.getSelectedLink(editor);

            if (element != null) {
                event.data.dialog = 'silvalink';
            };
        });
        // Dialog
        CKEDITOR.dialog.add('silvalink', this.path + 'dialogs/link.js');
    },
    afterInit: function(editor) {
        // Register a filter to displaying placeholders after mode change.

        var dataProcessor = editor.dataProcessor;
        var dataFilter = dataProcessor && dataProcessor.dataFilter;

        if (dataFilter) {
            dataFilter.addRules({
                elements: {
                    a: function(element) {
                        var attributes = element.attributes;
                        if (!attributes['class']) {
                            if (attributes['name']) {
                                attributes['class'] = 'anchor';
                            } else {
                                attributes['class'] = 'link';
                            };
                        };
                        if (!attributes['href']) {
                            attributes['href'] = 'javascript:void()';
                        } else {
                            if (!attributes['_silva_href'] && attributes['class'] == 'link') {
                                // Backup the href attribute into
                                // _silva_href: href get removed in
                                // case of copy and paste in some obscur cases.
                                attributes['_silva_href'] = attributes['href'];
                            };
                        };
                        return null;
                    }
                }
            });
        }
    }
});

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
    startDisabled : true
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
            var selection = editor.getSelection();
            if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                var selectedElement = selection.getSelectedElement();
                if (CKEDITOR.plugins.silvalink.isLink(selectedElement)) {
                    return selectedElement;
                };
            };

            var ranges = selection.getRanges(true)[0];
            ranges.shrink(CKEDITOR.SHRINK_TEXT);

            var base = ranges.getCommonAncestor();
            var selectedElement = base.getAscendant('a', true);
            if (CKEDITOR.plugins.silvalink.isLink(selectedElement)) {
                return selectedElement;
            };
            return null;
        }
        catch(e) {
            return null;
        }
    },
    insertAndSelectTextIfNoneSelected: function(editor, text) {
        var selection = editor.getSelection();
        var ranges = selection.getRanges(true);

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
              id: 'type',
              label: 'Link type',
              items: [
                  ['internal link', 'intern'],
                  ['external link', 'extern'],
                  ['local anchor', 'anchor']
              ],
              required: true,
              onChange: function () {
                  var value = this.getValue();
                  var dialog = this.getDialog();
                  var urlField = dialog.getContentElement('link', 'url').getElement();
                  var referenceField = dialog.getContentElement('link', 'linkedContent').getElement();
                  var documentAnchor = dialog.getContentElement('link', 'documentAnchor').getElement();
                  var anchor = dialog.getContentElement('link', 'anchor').getElement();

                  switch(value) {
                  case 'intern':
                      urlField.hide();
                      documentAnchor.hide();
                      referenceField.show();
                      anchor.show();
                      break;
                  case 'extern':
                      referenceField.hide();
                      documentAnchor.hide();
                      urlField.show();
                      anchor.show();
                      break;
                  default:
                      urlField.hide();
                      referenceField.hide();
                      anchor.hide();
                      documentAnchor.show();
                  };
              },
              setup: function(data) {
                  this.setValue(data.link.type);
              },
              commit: function(data) {
                  data.link.type = this.getValue();
              }
            },
            { type: 'text',
              id: 'url',
              label: 'External URL',
              required: true,
              setup: function(data) {
                  this.setValue(data.link.url);
              },
              validate: validatorDecorator(function() {
                  var dialog = this.getDialog();
                  var type = dialog.getContentElement('link', 'type').getValue();

                  if (type == 'extern') {
                      var checker = CKEDITOR.dialog.validate.regex(
                          /^(?:http|https|ftp|ftps|ssh|news|mailto|tel|webcal|itms):.*$/,
                          'You need to specify a valid external URL !');
                      return checker.apply(this);
                  };
                  return true;
              }),
              commit: function(data) {
                  data.link.url = this.getValue();
              }
            },
            { type: 'reference',
              id: 'linkedContent',
              label: 'Link target',
              required: true,
              onReferenceUpdate: function(event) {
                  var dialog = this.getDialog();
                  var title = dialog.getContentElement('link', 'title');

                  if (!title.getValue()) {
                      title.setValue(event.data.title);
                  };
              },
              validate: validatorDecorator(function() {
                  var dialog = this.getDialog();
                  var type = dialog.getContentElement('link', 'type').getValue();

                  if (type == 'intern') {
                      var checker = CKEDITOR.dialog.validate.notEmpty(
                          'You need to select a content to link to !');

                      return checker.apply(this);
                  };
                  return true;
              }),
              setup: function(data) {
                  if (data.link.content != undefined) {
                      this.setValue(data.link.content);
                  } else {
                      this.clear();
                  };
              },
              commit: function(data) {
                  data.link.content = this.getValue();
              }
            },
            { type: 'select',
              id: 'documentAnchor',
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
                  var type = dialog.getContentElement('link', 'type').getValue();

                  if (type == 'anchor') {
                      var checker = CKEDITOR.dialog.validate.notEmpty(
                          'You need to select a document anchor !');
                      return checker.apply(this);
                  };
                  return true;
              }),
              commit: function(data) {
                  var dialog = this.getDialog();
                  var type = dialog.getContentElement('link', 'type').getValue();

                  if (type == 'anchor') {
                      data.link.anchor = this.getValue();
                  };
              }
            },
            { type: 'text',
              id: 'anchor',
              label: 'Anchor',
              setup: function(data) {
                  this.setValue(data.link.anchor);
              },
              commit: function(data) {
                  var dialog = this.getDialog();
                  var type = dialog.getContentElement('link', 'type').getValue();

                  if (type != 'anchor') {
                      data.link.anchor = this.getValue();
                  };
              }
            },
            { type: 'select',
              id: 'target',
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
                  var dialog = this.getDialog();
                  var target = dialog.getContentElement('link', 'target');
                  var input = dialog.getContentElement('link', 'customTarget');

                  if (target.getValue() == 'input') {
                      input.getElement().show();
                  } else {
                      input.getElement().hide();
                  };
              },
              setup: function(data) {
                  var isCustom = true;
                  var items = this._.select.items;

                  for (var i = 0; i < items.length; i++) {
                      if (items[i][1] == data.link.target) {
                          isCustom = false;
                          break;
                      };
                  };
                  if (isCustom) {
                      var dialog = this.getDialog();
                      var customTarget = dialog.getContentElement(
                          'link', 'customTarget');

                      customTarget.setValue(data.link.target);
                      this.setValue('input');
                  } else {
                      this.setValue(data.link.target);
                  }
              },
              commit: function(data) {
                  var target = this.getValue();

                  if (target == 'input') {
                      var dialog = this.getDialog();
                      var customTarget = dialog.getContentElement('link', 'customTarget');

                      target = customTarget.getValue();
                  } else {
                      data.link.target = target;
                  }
              }
            },
            { type: 'text',
              id: 'customTarget',
              label: 'Custom target',
              required: true,
              validate: validatorDecorator(function() {
                  var dialog = this.getDialog();
                  var target = dialog.getContentElement('link', 'target').getValue();

                  if (target == 'input') {
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
              id: 'title',
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
