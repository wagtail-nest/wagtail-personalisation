(function($) {
    $(document).ready( () => {
        var count = $('.count_field');
        count.hide();

        var updateCountDispay = function(value) {
            if (value == 'dynamic') {
                count.slideUp(250);
            } else {
                count.slideDown(250);
            }
        };

        $('input:radio[name="type"]').change( event => {
            updateCountDispay(event.target.value);
        });
    });
})(jQuery);
