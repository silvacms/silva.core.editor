
CKEDITOR.plugins.add('silvalink', {
    requires: ['dialog', 'silvareference'],
    init: function(editor) {
        editor.addCommand(
            'silvalink',
            new CKEDITOR.dialogCommand('silvalink'));
        editor.ui.addButton('SilvaLink', {
            label : 'Link properties',
            command : 'silvalink',
            className: 'cke_button_link'
            });
        CKEDITOR.dialog.add('silvalink', this.path + 'dialogs/link.js');
    }
});

CKEDITOR.plugins.silvalink = {
    getSelectedLink: function(editor) {
        try {
            var selection = editor.getSelection();
            if (selection.getType() == CKEDITOR.SELECTION_ELEMENT) {
                var selectedElement = selection.getSelectedElement();
                if (selectedElement.is('a'))
                    return selectedElement;
            }

            var ranges = selection.getRanges(true)[0];
            ranges.shrink(CKEDITOR.SHRINK_TEXT);

            var root = ranges.getCommonAncestor();
            return root.getAscendant('a', true);
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
    createDialogFields: function () {
        // Define popup fields for links. They are defined here to be used in other plugins.
        return [
            { type: 'radio',
              id: 'type',
              label: 'Link type',
              items: [
                  ['internal link', 'intern'],
                  ['external link', 'extern'],
                  ['anchor', 'anchor']
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
              validate: function() {
                  var dialog = this.getDialog();
                  var type = dialog.getContentElement('link', 'type').getValue();

                  if (type == 'extern') {
                      var checker = CKEDITOR.dialog.validate.notEmpty(
                          'Missing link external URL');
                      return checker.apply( this );
                  };
                  return true;
              },
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
              hidden: true,
              required: true,
              setup: function(data) {
                  var editor = this.getDialog().getParentEditor();
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
              setup: function(data) {
                  this.setValue(data.link.anchor);
              },
              commit: function(data) {
                  data.link.anchor = this.getValue();
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
              validate: function() {
                  var dialog = this.getDialog();
                  var target = dialog.getContentElement('link', 'target').getValue();

                  if (target == 'input') {
                      var checker = CKEDITOR.dialog.validate.notEmpty(
                          'Custom window target is selected for the link, but no custom target is filled.');
                      return checker.apply(this);
                  };
                  return true;
              }
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
