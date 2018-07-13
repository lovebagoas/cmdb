$(document).ready(function () {
    init_approval_level();

});

function init_approval_level() {
    $('.weekday-start').select2({
        minimumResultsForSearch: Infinity,
        language: 'zh-CN',
        width: '100%',
        placeholder: '请选择',
    });
    $('.weekday-end').select2({
        minimumResultsForSearch: Infinity,
        language: 'zh-CN',
        width: '100%',
        placeholder: '请选择',
    });

    $('.form-control.input-small.timepicker').timepicker({
        minuteStep: 30,
        showMeridian: false,   // 24hr mode
        defaultTime: '0:00',
    });


    $('.level-select').select2({
        minimumResultsForSearch: Infinity,
        language: 'zh-CN',
        width: '100%',
        placeholder: '请选择',
    });
}

$('#createApprove').click(function () {
    document.getElementById('approveDetail').style.display = '';
    $("#approveList").removeClass("active");
    $("#tab-1").removeClass("active");
    $("#approveDetail").addClass("active");
    $("#tab-2").addClass("active");
});

$("#approveList").click(function () {
    document.getElementById('approveDetail').style.display = 'none';
    $("#approveDetail").removeClass("active");
    $("#tab-2").removeClass("active");
    $("#approveList").addClass("active");
    $("#tab-1").addClass("active");

});


