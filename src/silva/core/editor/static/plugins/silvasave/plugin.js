CKEDITOR.plugins.add('silvasave', {
  init: function(editor) {
    var pluginName = 'silvasave';

    editor.addCommand(pluginName, {
      exec: function(editor) {
        var base = $('head base').attr('href').replace('/edit', '');
        var service = base + '/++rest++silva.document.save';
        $.ajax({
          url: service,
          type: 'POST',
          data: {'content': editor.getData()},
          success: function(data){ editor.setData(data); },
          error: function(){ alert('an error happened while saving..')}
        });
      },
      canUndo: true
    });

    editor.ui.addButton('SilvaSave', {
        label: 'editor.plugin.save',
        command: pluginName,
        className: 'cke_button_save'
    });
  }
});
