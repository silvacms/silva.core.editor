
CKEDITOR.dialog.add('silvaanchor', function(editor) {

    return {
        title: 'Anchor properties',
        minWidth: 350,
        minHeight: 130,
        contents: [
            { id: 'anchor',
              elements: [
                  { type: 'text',
                    id: 'name',
                    label: 'Anchor name',
                    required: true
                  },
                  { type: 'text',
                    id: 'title',
                    label: 'Index title',
                    required: true
                  }
              ]
            }
        ]
    };
});
