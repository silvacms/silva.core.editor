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
                contentsCss: configuration['contents_css'],
                silvaFormats: configuration['formats'],
                extraPlugins: configuration['plugins'],
                removePlugins: 'save,link,flash,image,filebrowser,forms',
                skin: configuration['skin'],
                toolbar: 'Silva',
                toolbar_Silva: configuration['toolbars']
            });
        });
});
