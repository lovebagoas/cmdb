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
    let project_name = $('#project_name').val();
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
        allowClear: true,
        maximumSelectionLength: 4,
        minimumResultsForSearch: Infinity,
        language: 'zh-CN',
        width: '100%',
        placeholder: '请选择',
    });

    let env_id = $('#env_id').val();
    get_reboot_services(project_name, env_id);
}


$('#createPublish').click(function () {
    document.getElementById('createTab').style.display = '';
    $("#publishSheet").removeClass("active");
    $("#tab-2").removeClass("active");
    $("#createTab").addClass("active");
    $("#tab-3").addClass("active");
    init_tab3();
});

function delete_publishsheet(sheet_id) {
    let url = '/asset/publishsheet/delete/';
    let data = {
        'sheet_id': sheet_id,
    };
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        contentType: 'application/x-www-form-urlencoded',
        traditional: true,
        beforeSend: function () {
            // 禁用按钮防止重复提交
            $("#deleteSheetButton").attr({disabled: "disabled"});
        },
        success: function (result) {
            if (result.code === 0) {
                $("#" + sheet_id).remove();
            }
            else {
                alert(result.msg);
            }
            $("#deleteSheetButton").removeAttr("disabled");
            $("#deleteSheetModal").modal('hide');
            $("#page_loading").hide();
        },
        error: function () {
            alert('失败');
            $("#page_loading").hide();
            $("#deleteSheetButton").removeAttr("disabled");
        }
    });
}

function sheetRefuseReasonDetail(sheet_id) {
    let url = '/asset/publishsheet/reason/?sheet_id=' + sheet_id;
    $.ajax({
        url: url,
        type: "GET",
        success: function (result) {
            if (result.length > 0) {
                $("#refuse_reason_modal").html(result);
            }
        },
        error: function () {
            alert('失败');
        }
    });
}

function sheet_detail(sheet_id) {
    let url = '/asset/publishsheet/detail/?sheet_id=' + sheet_id;
    $.ajax({
        url: url,
        type: "GET",
        success: function (result) {
            if (result.length > 0) {
                $("#sheet_modal").html(result);
            }
        },
        error: function () {
            alert('失败');
        }
    });
}

function start_publish(sheet_id) {
    let url = '/asset/publishsheet/publish/start/';
    let data = {
        'sheet_id': sheet_id
    };
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        contentType: 'application/x-www-form-urlencoded',
        traditional: true,
        success: function (result) {
            if (result.code === 0) {
                alert('发布成功，请检查服务是否正常！！！');
            }
            else {
                alert(result.msg);
            }
            $("#page_loading").hide();
        },
        error: function () {
            alert('失败');
        }
    });
}

