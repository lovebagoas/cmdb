$(document).ready(function () {
    $('#project_select').select2({
        minimumResultsForSearch: Infinity,
        language: 'zh-CN',
        width: '100%',
        placeholder: '请选择',
    });

    $('#owner_select').select2({
        placeholder: '请选择',
        allowClear: true
    });
    $('#first_select').select2({
        placeholder: '请选择',
        allowClear: true
    });
    $('#second_select').select2({
        placeholder: '请选择',
        allowClear: true
    });
    $('#mailgroup_select').select2({
        placeholder: '请选择',
        allowClear: true
    });

    init_page();

});

function init_page() {
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

$('#add_level_select').click(function () {
    let level_obj = document.getElementsByClassName("select-level");
    // let level_str = level_obj[0].outerHTML;

    let append_str = " <div class='select-level ibox'>\n" +
        "                                                <div class='ibox-tools'>\n" +
        "                                                    <a class='close-level-set'>\n" +
        "                                                        <i class='fa fa-times' style='color: #ed5565'></i>\n" +
        "                                                    </a>\n" +
        "                                                </div>\n" +
        "\n" +
        "                                                <form role='form'>\n" +
        "                                                    <div class='row'>\n" +
        "                                                        <div class='col-lg-6'>\n" +
        "                                                            <div class='form-group'>\n" +
        "                                                                <label>起始日</label>\n" +
        "                                                                <select class='form-control weekday-start'>\n" +
        "                                                                    <option value=1>周一</option>\n" +
        "                                                                    <option value=2>周二</option>\n" +
        "                                                                    <option value=3>周三</option>\n" +
        "                                                                    <option value=4>周四</option>\n" +
        "                                                                    <option value=5>周五</option>\n" +
        "                                                                    <option value=6>周六</option>\n" +
        "                                                                    <option value=7>周日</option>\n" +
        "                                                                </select>\n" +
        "                                                            </div>\n" +
        "                                                        </div>\n" +
        "                                                        <div class='col-lg-6'>\n" +
        "                                                            <div class='form-group'>\n" +
        "                                                                <label>截止日</label>\n" +
        "                                                                <select class='form-control weekday-end'>\n" +
        "                                                                    <option value=1>周一</option>\n" +
        "                                                                    <option value=2>周二</option>\n" +
        "                                                                    <option value=3>周三</option>\n" +
        "                                                                    <option value=4>周四</option>\n" +
        "                                                                    <option value=5>周五</option>\n" +
        "                                                                    <option value=6>周六</option>\n" +
        "                                                                    <option value=7 selected>周日</option>\n" +
        "                                                                </select>\n" +
        "                                                            </div>\n" +
        "                                                        </div>\n" +
        "                                                    </div>\n" +
        "\n" +
        "                                                    <div class='row'>\n" +
        "                                                        <div class='col-lg-6'>\n" +
        "                                                            <div class='form-group'>\n" +
        "                                                                <label>起始时间</label>\n" +
        "                                                                <div class='input-group bootstrap-timepicker timepicker'>\n" +
        "                                                                    <input type='text'\n" +
        "                                                                           class='form-control input-small timepicker start-time'>\n" +
        "                                                                    <span class='input-group-addon'><i\n" +
        "                                                                            class='glyphicon glyphicon-time'></i></span>\n" +
        "                                                                </div>\n" +
        "                                                            </div>\n" +
        "                                                        </div>\n" +
        "                                                        <div class='col-lg-6'>\n" +
        "                                                            <div class='form-group'>\n" +
        "                                                                <label>截止时间</label>\n" +
        "                                                                <div class='input-group bootstrap-timepicker timepicker'>\n" +
        "                                                                    <input type='text'\n" +
        "                                                                           class='form-control input-small timepicker end-time'>\n" +
        "                                                                    <span class='input-group-addon'><i\n" +
        "                                                                            class='glyphicon glyphicon-time'></i></span>\n" +
        "                                                                </div>\n" +
        "                                                            </div>\n" +
        "                                                        </div>\n" +
        "                                                    </div>\n" +
        "\n" +
        "                                                    <div class='row'>\n" +
        "                                                        <div class='col-lg-12'>\n" +
        "                                                            <div class='form-group'>\n" +
        "                                                                <label>审批级别</label>\n" +
        "                                                                <select class='form-control level-select'>\n" +
        "                                                                    <option value='1' selected>无需审批</option>\n" +
        "                                                                    <option value='2'>一级审批</option>\n" +
        "                                                                    <option value='3'>二级审批</option>\n" +
        "                                                                </select>\n" +
        "                                                            </div>\n" +
        "                                                        </div>\n" +
        "                                                    </div>\n" +
        "                                                </form>\n" +
        "                                                <br>\n" +
        "                                            </div> ";


    $('#level_select').append(append_str);
    init_page();
    $('.close-level-set').click(function () {
        let content = $(this).closest('div.ibox');
        if (level_obj.length != 1) {
            content.remove();
        }
        else {
            return false;
        }
    });
});

$('#create_projectinfo').click(function () {
    let project_select = $('#project_select').val();
    let owner_select_list = $('#owner_select').val();
    let first_select_list = $('#first_select').val();
    let second_select_list = $('#second_select').val();
    let mailgroup_select_list = $('#mailgroup_select').val();

    if (!project_select || !owner_select_list) {
        alert("必填内容不能为空 ！");
        return false;
    }

    let weekday_start_list = $('.weekday-start');
    let weekday_end_list = $('.weekday-end');
    let time_start_list = $('.start-time');
    let time_end_list = $('.end-time');
    let level_select_list = $('.level-select');
    let level_list = [];
    weekday_start_list.each(function (index, el) {
        level_list.push([el.value, weekday_end_list[index].value, time_start_list[index].value, time_end_list[index].value, level_select_list[index].value]);
    });

    let url = '/asset/createProject/';
    let data = {
        'project_id': project_select,
        'owner_select_list': owner_select_list,
        'first_select_list': first_select_list,
        'second_select_list': second_select_list,
        'mailgroup_select_list': mailgroup_select_list,
        'level_list': level_list,
    };
    $.ajax({
            url: url,
            type: "POST",
            data: data,
            contentType: 'application/x-www-form-urlencoded',
            traditional: true,
            beforeSend: function () {
                // 禁用按钮防止重复提交
                $("#create_projectinfo").attr({disabled: "disabled"});
                $("#page_loading").show();
            },
            success: function (result) {
                if (result.code === 0) {
                    window.location.reload();
                }
                else {
                    alert(result.msg);
                    $("#create_projectinfo").removeAttr("disabled");
                }
                $("#page_loading").hide();
            },
            error: function () {
                alert('失败');
                $("#create_projectinfo").removeAttr("disabled");
                $("#page_loading").hide();
            }
        });
});

function sendProjectValue(project_name) {
    $("#project_name").val(project_name);
    
}
