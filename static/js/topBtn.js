$(document).ready(function () {

    $(".return-top").hide(); // 탑 버튼 숨김
    $(function () {

        $(window).scroll(function () {
            if ($(this).scrollTop() > 100) { // 스크롤 내릴 표시
                $('.return-top').fadeIn();
            } else {
                $('.return-top').fadeOut();
            }
        });

        $('.return-top').click(function () {
            $('body,html').animate({
                scrollTop: 0
            }, 10); // 탑 이동 스크롤 속도
            return false;
        });
    });

});