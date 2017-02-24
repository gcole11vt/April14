window.Automation = {};
window.Automation.initialize = function () {
    $('input[name="text"]').on('keypress', function () {
        $('.has-error').hide();
    });
};
