/*
	Alright, we're almost there. The only thing that's wrong now is that the variables
	"lineChart" and "pieChart" don't exist in the scope of the ajax method at the bottom of
	the page. what would be a solution?

	What happens if I define them here as globals, and then simply assign a value to them
	in the main script? would that work?


	IT DID IT! HELL YEAH IT DID IT, FUCK MOTHERFUCKING YEAH! WOOO, THIS IS AWESOME!

*/

var lineChart;
var pieChart;


var lineChartContext = $("#lineChartCanvas");
var pieChartContext = $("#pieChartCanvas");

// ow do I guarantee that the length of the date range, the dailyIn array,
// and the dailyOut array 
function calculateDailyChange(start, posChange, negChange){
    let sumArray = [];
    let runningSum = parseFloat(start);

    //both posChange and negChange should be arrays of the same length

    // hacky, I'm just pulling one length arbitrarily
    for (var i = 0; i < posChange.length; i++){
        runningSum += parseFloat(posChange[i])+parseFloat(negChange[i]);
        sumArray.push(runningSum);
    }

    return sumArray;
}

function drawLinechart(startingMoney, dailyIn, dailyOut, labelsArray, context){
    var currentSum = calculateDailyChange(startingMoney, dailyIn, dailyOut);

    var lineChartData = {
        labels: labelsArray,
        datasets: [{
            data: dailyIn,
            label: "Money In",
            fill: false,
            borderColor: "rgb(50, 211, 69)"
        }, {
            data: dailyOut,
            label: "Money Out",
            fill: false,
            borderColor: "rgb(210, 49, 49)"
        }, {
            data: currentSum,
            label: "Daily Sum",
            fill: false,
            borderColor: "rgb(66, 134, 244)"
        }]
    }

    var lineChartOptions = {
        responsive: true,
        // for some reason this is making the chart go nuts
        //maintainAspectRatio: false,
        legend: { display: false },

        elements: {
            line: { 
                tension: .05
            }
        }
    };

    return new Chart(lineChartContext, {
        type: 'line',
        data: lineChartData,
        options: lineChartOptions, 
    });
}



/*
    TODO: There's a weird thing happening how where the labels aren't lining up. When
    you hover over sections of the pie chart they reveal the label for one of the adjacent
    slices but not the one you're hovering over - does it have something to do with using
    the response: true option?

    Figure out a color scheme to use and implement these.

	What happens when there are less than 8 categories?
*/


function drawPieChart(labelsArray, valuesArray, context){
    var pieChartData = {
        labels: labelsArray,
        datasets: [{
        	/*	
        		Change these colors in the future to match color scheme/use variables
        		rather than hardcoded hex 
        	*/
        	backgroundColor: [
	            "#2ecc71",
	            "#3498db",
	            "#95a5a6",
	            "#9b59b6",
	            "#f1c40f",
	            "#e74c3c",
	            "#34495e"
	          ],
            data: valuesArray 
        }]
    };

    var pieChartOptions = {
        responsive: true,
    };

    return new Chart(pieChartContext, {
        type: 'pie',
        data: pieChartData,
        options: pieChartOptions,
    });

}


$(document).ready(function(){
	const DEBUG = true;


	// function to check if HTTP method requires use of CSRF token
	function csrfSafeMethod(method) {
		return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}

	// set ajax header to for non-csrf safe HTTP methods
	$.ajaxSetup({
		beforeSend: function(xhr, settings){
			if (!csrfSafeMethod(settings.type) && !this.crossDomain){
				xhr.setRequestHeader("X-CSRFToken", Cookies.get("csrftoken"));
			}
		}
	});

	function redrawCharts(){
		$.ajax({
            url: "/",
            type: "GET",
            success: function(data){
                console.log("Everything's working fine");

                console.log(data);

                // destroy and redraw the charts
                lineChart.destroy();
                pieChart.destroy();
                
                lineChart = drawLinechart(data.initial_funds, data.pos_change_vals, data.neg_change_vals,
                    data.dates_in_range, $("#lineChartCanvas"));
                pieChart = drawPieChart(data.sorted_expense_cat, data.sorted_expense_val, 
                    $("#pieChartCanvas"));

                $("#money-total").html(data.current_funds)
            },
        });
	}

	$("a.section-toggle-link").on("click", function(event){
		event.preventDefault();

		var target = $(this).attr("toggle-target");
		
		if (DEBUG)
			console.log("click event recorded, toggling " + target + "...");

		$("#" + target).slideToggle(300);

		if (DEBUG)
			console.log("Toggle completed.");
	});


	// handler for transaction form
	$("#transactionForm").on("submit", function(event){
		event.preventDefault();
		if (DEBUG)
			console.log("#transactionForm submitted.");

		var transValue 	= $(this).find("#id_value").val();
		var transMemo  	= $(this).find("#id_memo").val();
		var transCat   	= $(this).find("#categoryString").val();

		console.log(transValue + " " + transMemo + " " + transCat);

		$.ajax({
			url: "transaction/add",
			context: this,
			data: {
				value: transValue,
				memo: transMemo,
				category_string: transCat
			},
			type: 'POST',
			success: function(data){
				if (DEBUG)
					console.log(data.success + ": " + data.message);

				var resultRow = $(data.transactionHtml).insertAfter("#transaction-table tr:first");
				$("#transactionForm").trigger("reset");

				redrawCharts();
			}
		});
	});

	//handler for delete buttons
	$(".transaction-delete-button").on("click", function(event){
		event.preventDefault();
		var transactionTarget = $(this).attr("delete-target");

		if (DEBUG)
			console.log("Deleting transaction " + transactionTarget + "...");

		$.ajax({
			url: "transaction/delete",
			data: {"transaction_pk": transactionTarget},
			type: "POST",
			success: function(data){
				console.log(data);

				$("#transaction-" + transactionTarget).remove();
				redrawCharts();
			}
		});
	});
});
