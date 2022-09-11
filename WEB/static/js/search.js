$(document).ready(function() {


	$("#search").keyup(function() {

		var k = $(this).val();


		$("#board_table > tbody > tr").hide();

		

		var title = $("#board_table > tbody > tr > td:nth-child(5n+1):contains('" + k + "')");

		var id = $("#board_table > tbody > tr > td:nth-child(5n+2):contains('" + k + "')");

        var num = $("#board_table > tbody > tr > td:nth-child(5n+3):contains('" + k + "')");

        var money = $("#board_table > tbody > tr > td:nth-child(5n+4):contains('" + k + "')");



        $(title).parent().show();

        $(id).parent().show();

        $(num).parent().show();

        $(money).parent().show();

    })

});