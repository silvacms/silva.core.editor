$(document).ready(function(){
    var content_url = $('#content-url').attr('href');
    var text = $('#editor textarea');
    var lang = $('html').attr('lang');

    if (!lang) {
        lang = 'en';
    };

    $.each($('div.externalsource', $(text)), function(index, item) {
      $(item).attr('contenteditable', 'false');
    });

    $.getJSON(
        content_url + '/++rest++silva.core.editor.configuration',
        function(configuration) {
            for (var name in configuration['paths']) {
                CKEDITOR.plugins.addExternal(name, configuration['paths'][name]);
            };
            text.ckeditor(function(){}, {
                entities: false,
                fullPage: false,
                language: lang,
                extraPlugins: configuration['extraPlugins'],
                removePlugins: 'save,link,flash,image',
                skin: configuration['skin'],
                toolbar: 'Silva',
                toolbar_Silva: configuration['toolbars']
            });
        });
});
