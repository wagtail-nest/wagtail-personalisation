(function($) {
    $(document).ready( () => {
        var count = $('.count_field');
        var typeRadio = $('input:radio[name="type"]');

        var updateCountDispay = function(value) {
            if (value == 'dynamic') {
                count.slideUp(250);
            } else {
                count.slideDown(250);
            }
        };

        updateCountDispay(typeRadio.filter(':checked').val());

        typeRadio.change( event => {
            updateCountDispay(event.target.value);
        });
    });
})(jQuery);
