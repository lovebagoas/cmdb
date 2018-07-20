$(document).ready(function () {
    init_tab1();
});

function init_tab1() {
    $('#project_select').select2({
        placeholder: '请选择',
        allowClear: true
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
            if (result.length > 0) {
                $("#publish_sheet").html(result);
            }
            $("#page_loading").hide();
        },
        error: function () {
            alert('失败');
            $("#page_loading").hide();
        }
    });
}

$("#projectInfo").click(function () {
    document.getElementById('createTab').style.display = 'none';
    document.getElementById('doneSheet').style.display = 'none';
    document.getElementById('initTemplate').style.display = 'none';
    $("#publishSheet").removeClass("active");
    $("#tab-2").removeClass("active");
    $("#createTab").removeClass("active");
    $("#tab-3").removeClass("active");
    $("#projectInfo").addClass("active");
    $("#tab-1").addClass("active");
    $("#doneSheet").removeClass("active");
    $("#tab-4").removeClass("active");
    init_tab1();
    $("#initTemplate").removeClass("active");
    $("#tab-5").removeClass("active");
    $("#approvalLevelList").removeClass("active");
    $("#tab-6").removeClass("active");
});

$("#publishSheet").click(function () {
    document.getElementById('createTab').style.display = 'none';
    document.getElementById('doneSheet').style.display = 'none';
    document.getElementById('initTemplate').style.display = 'none';
    $("#projectInfo").removeClass("active");
    $("#tab-1").removeClass("active");
    $("#createTab").removeClass("active");
    $("#tab-3").removeClass("active");
    $("#publishSheet").addClass("active");
    $("#tab-2").addClass("active");
    $("#doneSheet").removeClass("active");
    $("#tab-4").removeClass("active");
    init_tab2();
    $("#initTemplate").removeClass("active");
    $("#tab-5").removeClass("active");
    $("#approvalLevelList").removeClass("active");
    $("#tab-6").removeClass("active");
});


$('#create_projectinfo').click(function () {
    let project_select_list = $('#project_select').val();
    let owner_select_list = $('#owner_select').val();
    let first_select_list = $('#first_select').val();
    let second_select_list = $('#second_select').val();
    let mailgroup_select_list = $('#mailgroup_select').val();

    if (!project_select_list || !owner_select_list) {
        alert("必填内容不能为空 ！");
        return false;
    }
    let data = {
        'project_select_list': project_select_list,
        'owner_select_list': owner_select_list,
        'first_select_list': first_select_list,
        'second_select_list': second_select_list,
        'mailgroup_select_list': mailgroup_select_list,
    };


    let url = '/asset/project/init/create/';
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
                window.location.reload();
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

function sendValue(timeslot_id) {
    $("#timeslot_id").val(timeslot_id);

}

$("#create_publishsheet").click(function () {
    let project_name = $('#project_name').val();
    let env_id = $('#env_id').val();
    let tapd_url = $('#tapd_url').val();
    let reboot_services_list = $('#reboot_services_choice').val();
    let publish_date = $('#datepicker').datepicker('getData').val();
    let publish_time = $('#publish_time').val();
    let sql = $('#sql').val();
    let consul_key = $('#consul_key').val();

    if (!project_name || !env_id || !reboot_services_list || !publish_date || !publish_time || !tapd_url || !sql || !consul_key) {
        alert('必填内容不能为空');
        return false;
    }

    if (tapd_url.match("tower.im") || tapd_url.match("tapd.cn")) {
        console.log('url ok');
    }
    else {
        alert('TAPD URL格式不正确');
        return false;
    }

    let url = '/asset/publishsheet/create/';
    let data = {
        'project_name': project_name,
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

$("#done_sheets").click(function () {
    document.getElementById('createTab').style.display = 'none';
    document.getElementById('initTemplate').style.display = 'none';
    document.getElementById('doneSheet').style.display = '';
    $("#projectInfo").removeClass("active");
    $("#tab-1").removeClass("active");
    $("#publishSheet").removeClass("active");
    $("#tab-2").removeClass("active");
    $("#createTab").removeClass("active");
    $("#tab-3").removeClass("active");
    $("#initTemplate").removeClass("active");
    $("#tab-5").removeClass("active");

    $("#doneSheet").addClass("active");
    $("#tab-4").addClass("active");
    init_tab4();
    $("#approvalLevelList").removeClass("active");
    $("#tab-6").removeClass("active");
});


function init_tab4() {
    let url = '/asset/publishsheet/list/done/';
    $.ajax({
        url: url,
        type: "GET",
        beforeSend: function () {
            $("#page_loading").show();
        },
        success: function (result) {
            if (result.length > 0) {
                $("#done_outtime_sheet").html(result);
            }
            $("#page_loading").hide();
        },
        error: function () {
            alert('失败');
            $("#page_loading").hide();
        }
    });
}

$("#template_init").click(function () {
    document.getElementById('createTab').style.display = 'none';
    document.getElementById('doneSheet').style.display = 'none';
    document.getElementById('initTemplate').style.display = '';
    $("#projectInfo").removeClass("active");
    $("#tab-1").removeClass("active");
    $("#publishSheet").removeClass("active");
    $("#tab-2").removeClass("active");
    $("#createTab").removeClass("active");
    $("#tab-3").removeClass("active");
    $("#doneSheet").removeClass("active");
    $("#tab-4").removeClass("active");

    $("#initTemplate").addClass("active");
    $("#tab-5").addClass("active");
    init_tab5();
    $("#approvalLevelList").removeClass("active");
    $("#tab-6").removeClass("active");
});

function init_tab5() {
    let url = '/asset/project/template/list/';
    $.ajax({
        url: url,
        type: "GET",
        beforeSend: function () {
            $("#page_loading").show();
        },
        success: function (result) {
            if (result.length > 0) {
                $("#init_template").html(result);
            }
            $("#page_loading").hide();
        },
        error: function () {
            alert('失败');
            $("#page_loading").hide();
        }
    });
}

$("#approvalLevelList").click(function () {
    document.getElementById('createTab').style.display = 'none';
    document.getElementById('doneSheet').style.display = 'none';
    document.getElementById('initTemplate').style.display = 'none';
    $("#projectInfo").removeClass("active");
    $("#tab-1").removeClass("active");
    $("#publishSheet").removeClass("active");
    $("#tab-2").removeClass("active");
    $("#createTab").removeClass("active");
    $("#tab-3").removeClass("active");
    $("#doneSheet").removeClass("active");
    $("#tab-4").removeClass("active");
    $("#initTemplate").removeClass("active");
    $("#tab-5").removeClass("active");

    $("#approvalLevelList").addClass("active");
    $("#tab-6").addClass("active");
    init_tab6();
});

function init_tab6() {
    let url = '/asset/project/level/list/';
    $.ajax({
        url: url,
        type: "GET",
        beforeSend: function () {
            $("#page_loading").show();
        },
        success: function (result) {
            if (result.length > 0) {
                $("#approval_level_list").html(result);
            }
            $("#page_loading").hide();
        },
        error: function () {
            alert('失败');
            $("#page_loading").hide();
        }
    });
}

function delete_projectinfo(projectinfo_id) {
    let url = '/asset/project/init/delete/';
    let data = {
        'projectinfo_id': projectinfo_id,
    };
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        contentType: 'application/x-www-form-urlencoded',
        traditional: true,
        beforeSend: function () {
            // 禁用按钮防止重复提交
            $("#deleteProjectButton").attr({disabled: "disabled"});
        },
        success: function (result) {
            if (result.code === 0) {
                $("#" + projectinfo_id).remove();
            }
            else {
                alert(result.msg);
            }
            $("#deleteProjectButton").removeAttr("disabled");
            $("#deleteProjectModal").modal('hide');
        },
        error: function () {
            alert('失败');
            $("#deleteProjectButton").removeAttr("disabled");
        }
    });
}
