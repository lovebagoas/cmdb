$(document).ready(function () {
    init_tab2();
    init_approval_level();

});

function init_tab1() {
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
}

function init_tab2() {
    let url = '/asset/publishsheet/list/';
    $.ajax({
        url: url,
        type: "GET",
        beforeSend: function () {
            $("#page_loading").show();
        },
        success: function (result) {
            if (result.code === 0) {
                console.log(result.content);
            }
            else {
                alert(result.msg);
            }
            $("#page_loading").hide();
        },
        error: function () {
            alert('失败');
            $("#page_loading").hide();
        }
    });
}

function get_reboot_services(project_name, env_id) {
    $('#reboot_services_choice').val(null).trigger('change');
    $('#reboot_services_choice').on("removed", function () {
    });
    let old_obj = document.getElementById('reboot_services_choice');
    old_obj.options.length = 0;
    $.getJSON("/asset/getProjectList", {"project": project_name, "env": env_id}, function (result) {
        console.log(result);
        console.log(result.length);
        for (let i = 0; i < result.length; i++) {
            let newOption = new Option(result[i], result[i], false, false);
            $('#reboot_services_choice').append(newOption).trigger('change');
        }
    });
}

function init_tab3() {
    $('#datepicker').parent().datepicker({
        autoclose: true,
        todayHighlight: true,
        format: "yyyy-mm-dd",
        language: "zh-CN",
        startDate: "today",
    });

    $('#publish_time').timepicker({
        minuteStep: 5,
        showMeridian: false,   // 24hr mode
        defaultTime: '12:00',
    });

    $('#project_name').select2({
        placeholder: '请选择',
    });

    $('#project_name').on("change", function () {
        let project_name = $(this).val();
        let env_id = $('#env_id').val();
        get_reboot_services(project_name, env_id);
    });

    $('#env_id').select2({
        minimumResultsForSearch: Infinity,
        placeholder: '请选择',
    });

    $('#env_id').on("change", function () {
        let project_name = $('#project_name').val();
        let env_id = $(this).val();
        get_reboot_services(project_name, env_id);
    });

    $('#reboot_services_choice').select2({
        minimumResultsForSearch: Infinity,
        language: 'zh-CN',
        width: '100%',
        placeholder: '请选择',
    });

    let project_name = $('#project_name').val();
    let env_id = $('#env_id').val();
    get_reboot_services(project_name, env_id);
}

$("#projectInfo").click(function () {
    document.getElementById('createTab').style.display = 'none';
    $("#publishSheet").removeClass("active");
    $("#tab-2").removeClass("active");
    $("#createTab").removeClass("active");
    $("#tab-3").removeClass("active");
    $("#projectInfo").addClass("active");
    $("#tab-1").addClass("active");
    init_tab1();
});

$("#publishSheet").click(function () {
    document.getElementById('createTab').style.display = 'none';
    $("#projectInfo").removeClass("active");
    $("#tab-1").removeClass("active");
    $("#createTab").removeClass("active");
    $("#tab-3").removeClass("active");
    $("#publishSheet").addClass("active");
    $("#tab-2").addClass("active");
    init_tab2();
});

$('#createPublish').click(function () {
    document.getElementById('createTab').style.display = '';
    $("#publishSheet").removeClass("active");
    $("#tab-2").removeClass("active");
    $("#createTab").addClass("active");
    $("#tab-3").addClass("active");
    init_tab3();
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
        'project_name': project_select,
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

$("#create_publishsheet").click(function () {
    let project_name = $('#project_name').val();
    let env_id = $('#env_id').val();
    let tapd_url = $('#tapd_url').val();
    let reboot_services_list = $('#reboot_services_choice').val();
    let publish_date = $('#datepicker').datepicker('getData').val();
    let publish_time = $('#publish_time').val();
    if (!project_name || !env_id || !reboot_services_list || !publish_date || !publish_time || !tapd_url) {
        alert('必填内容不能为空');
        return false;
    }
    let sql = $('#sql').val();
    let consul_key = $('#consul_key').val();

    let url = '/asset/publishsheet/create/';
    let data = {
        'env_id': env_id,
        'tapd_url': tapd_url,
        'reboot_services_list': reboot_services_list,
        'publish_date': publish_date,
        'publish_time': publish_time,
        'sql': sql,
        'consul_key': consul_key,
    };
    console.log(data);
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        contentType: 'application/x-www-form-urlencoded',
        traditional: true,
        beforeSend: function () {
            // 禁用按钮防止重复提交
            $("#create_publishsheet").attr({disabled: "disabled"});
            $("#page_loading").show();
        },
        success: function (result) {
            if (result.code === 0) {
                window.location.reload();
            }
            else {
                alert(result.msg);
                $("#create_publishsheet").removeAttr("disabled");
            }
            $("#page_loading").hide();
        },
        error: function () {
            alert('失败');
            $("#create_publishsheet").removeAttr("disabled");
            $("#page_loading").hide();
        }
    });
});
