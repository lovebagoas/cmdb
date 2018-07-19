$(document).ready(function () {
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

function agreeButton(publish_id) {
    let agree_text = "";
    let url = "/asset/approve/judge/";
    let data = {
        'publish_id': publish_id,
        'approve': '1',
        'text': agree_text,
    };
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        contentType: 'application/x-www-form-urlencoded',
        traditional: true,
        success: function (result) {
            if (result.code === 0) {
                window.location.reload();
            }
            else {
                alert(result.msg);
            }
        },
        error: function () {
            alert('失败');
        }
    });
}

function refuseButton(publish_id) {
    let refuse_text = $("#refuse_text").val();
    if (!refuse_text) {
        alert("拒绝理由必填");
        return false;
    }
    let url = "/asset/approve/judge/";
    let data = {
        'publish_id': publish_id,
        'approve': '2',
        'text': refuse_text,
    };
    $.ajax({
        url: url,
        type: "POST",
        data: data,
        contentType: 'application/x-www-form-urlencoded',
        traditional: true,
        success: function (result) {
            if (result.code === 0) {
                window.location.reload();
            }
            else {
                alert(result.msg);
            }
        },
        error: function () {
            alert('失败');
        }
    });
}
