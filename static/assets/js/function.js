console.log("Working fine");

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

$("#commentForm").submit(function (e) {
    e.preventDefault();

    let dt = new Date();
    let time = dt.getDay() + " " + monthNames[dt.getUTCMonth()] + ", " + dt.getFullYear()

    $.ajax({
        data: $(this).serialize(),

        method: $(this).attr("method"),

        url: $(this).attr("action"),

        dataType: "json",

        success: function (response) {
            console.log("Comment Saved to DB..");

            if (response.bool == true) {
                $("#review-res").html("Review added successfully.")
                $(".hide-comment-form").hide()
                $(".add-review").hide()

                let _html = '<div class="single-comment justify-content-between d-flex mb-30">'
                _html += '<div class="user justify-content-between d-flex">'
                _html += '<div class="thumb text-center">'
                _html += '<img src="https://media.istockphoto.com/id/1495088043/vector/user-profile-icon-avatar-or-person-icon-profile-picture-portrait-symbol-default-portrait.jpg?s=612x612&w=0&k=20&c=dhV2p1JwmloBTOaGAtaA3AW1KSnjsdMt7-U_3EZElZ0=" alt="" />'
                _html += '<a href="#" class="font-heading text-brand">' + response.context.user + '</a>'
                _html += '</div>'

                _html += '<div class="desc">'
                _html += '<div class="d-flex justify-content-between mb-10">'
                _html += '<div class="d-flex align-items-center">'
                _html += '<span class="font-xs text-muted">' + time + '</span>'
                _html += '</div>'

                for (let i = 1; i <= response.context.rating; i++) {
                    _html += "<i class='fas fa-star text-warning'></i>"
                }
                _html += '</div>'
                _html += '<p class="mb-10">' + response.context.review + '</p>'

                _html += '</div>'
                _html += '</div>'
                _html += '</div>'


                $(".comment-list").prepend(_html)
            }
        }
    })
})