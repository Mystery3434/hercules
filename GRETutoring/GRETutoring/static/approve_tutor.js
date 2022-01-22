$(document).ready(function($) {
    
    $('[id^=approve]').on('click', function(){
        console.log("CLICEKD");
        console.log(this.id);
        const tutor_application_id = this.id.split("_")[1];
        console.log(tutor_application_id);
        const approved_application_id = {'application_id' : tutor_application_id};
        console.log($.ajax);
        $.ajax({
                type: "POST",
                contentType: "application/json;charset=utf-8",
                url: "/pending_tutor_applications",
                traditional: "true",
                data: JSON.stringify({approved_application_id}),
                dataType: "json"
                });

            
    });
});