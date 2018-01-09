var lineChart;
var pieChart;

var lineChartContext = $("#lineChartCanvas");
var pieChartContext = $("#pieChartCanvas");

var sb_animSpeed = 200;


// how do I guarantee that the length of the date range, the dailyIn array,
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
		var dateRangeData = $("#date-range").datepicker().data('datepicker');

		$.ajax({
            url: "/",
            data: {
            	date_range_start: dateRangeData.minRange.toISOString(),
            	date_range_end: dateRangeData.maxRange.toISOString(),
            },
            type: "GET",
            success: function(data){
            	if (DEBUG)
                	console.log(data);

                // destroy and redraw the charts
                lineChart.destroy();
                pieChart.destroy();
                
                lineChart = drawLinechart(data.range_start_funds, data.pos_change_vals, data.neg_change_vals,
                    data.dates_in_range, $("#lineChartCanvas"));
                pieChart = drawPieChart(data.sorted_expense_cat, data.sorted_expense_val, 
                    $("#pieChartCanvas"));

                // fill new stat values
                for (var i = 0; i < data.statistics_list.length; i++)
                	$("#stat-" + data.statistics_list[i].id).html(data.statistics_list[i].value);

                $("#money-total").html(data.current_funds);
            },
        });
	}

	//handler for delete buttons
	function bindDeleteButtonEvents(){
		console.log("calling bindDeleteButtonEvents()...");

		$(".transaction-delete-button").on("click", function(event){
			event.preventDefault();

			var transactionTarget = $(this).attr("delete-target");

			if (DEBUG)
				console.log("Deleting transaction " + transactionTarget + "...");

			$.ajax({
				url: "/transaction/delete",
				data: {"transaction_pk": transactionTarget},
				type: "POST",
				success: function(data){
					console.log(data);

					$("#transaction-" + transactionTarget).remove();
					$("#money-total").html(data.current_funds);

					redrawCharts();
				}
			});
		});
	}

	bindDeleteButtonEvents();

	function scrollToTop(){
		// maybe slower than the anim speed?
		$("html, body").animate({scrollTop: 0}, sb_animSpeed);
		return true;
	}
	// event listeners for toolbar

	// add transaction
	$("#global-new-transaction").on("click", function(event){
		event.preventDefault();
		scrollToTop();
		$("#transaction-jumbotron").slideToggle(sb_animSpeed);
	});

	// datepicker
	$("#global-calendar").on("click", function(event){
		event.preventDefault();

		/*
			I think I finally wrapped up this nonsense. Rather than trying to make sure we made a rule that matched
			and ignored click events on any child of #global-calendar that we didn't want triggering this event,
			I simply added ".global-calendar-toggle" to the only elements that I want to trigger this event. So now
			we capture the event and double check that it has the class and only apply the toggle action if it does.
		*/

		if ($(event.target).hasClass("global-calendar-toggle"))
			$("#global-calendar-container").fadeToggle(sb_animSpeed);
	});

	// toggle page charts
	$("#global-chart-toggle").on("click", function(event){
		event.preventDefault();
		scrollToTop();
		$("#charts-jumbotron").slideToggle(sb_animSpeed);
	});


	// pretty sure this is all obsolete now, going to mark this to be removed.

	/*
	$("a.section-toggle-link").on("click", function(event){
		event.preventDefault();

		// is there a way to synchronize all of these animations better?
		// I want to stage it so it scrolls, then after that the rest of the code executes.

		$("html, body").animate({scrollTop: 0}, "slow");

		var target = $("#"+$(this).attr("toggle-target"));

		if (DEBUG)
			console.log("click event recorded, toggling " + target + "...");

		// check for and untoggle previously toggled element
		$(".section-toggle-link").each(function(){
			var currentElement = $("#" + $(this).attr("toggle-target"));


			console.log(target.attr("id"));
			console.log(currentElement.attr("id"));
			console.log("is target id equal to currentElement id? " + (target.attr("id") == currentElement.attr("id")));
			console.log("-----");

			// toggle and hide current element 
			if (currentElement.is(":visible") && currentElement.attr("id") != target.attr("id"))
				currentElement.slideToggle(300);
		});

		target.slideToggle(300);

		if (DEBUG)
			console.log("Toggle completed.");
	});
	*/

	// handler for transaction form
	$("#transaction-form").on("submit", function(event){
		event.preventDefault();
		if (DEBUG)
			console.log("#transaction-form submitted.");

		var targetURL = $(this).attr("action");

		var transValue = $(this).find("#id_value").val();
		var transMemo = $(this).find("#id_memo").val();
		var transCat = $(this).find("#category-string").val();
		//var transDate = $(this).find("#date-string").datepicker().data('datepicker').date.toISOString();
		/* 
			this doesn't seem like the best way to do this, but the above method isn't working. No clue why.
			I'm running into the same problem in the devtools console - I can keep pulling the date from 
			datepicker().data('datepicker'), but it doesn't update when the date changes. 
		*/
		var transDate = new Date($(this).find("#date-string").val()).toISOString();

		console.log(transValue + " " + transMemo + " " + transCat + " " + transDate);

		$.ajax({
			url: targetURL,
			context: this,
			data: {
				value: transValue,
				memo: transMemo,
				category_string: transCat,
				date_string: transDate
			},
			type: 'POST',
			success: function(data){
				if (DEBUG)
					console.log(data.success + ": " + data.message);

				var dateRangeData = $("#date-range").datepicker().data('datepicker');

				//make sure it exists within bounds to add
				if (moment(data.transactionDate).isAfter(dateRangeData.selectedDates[0]) 
					&& moment(data.transactionDate).isBefore(dateRangeData.selectedDates[1])) {
					// find spot to add row
					var adjacentRow;

					$($(".transaction-table-row").get().reverse()).each(function(){
						var rowDate = $(this).find(".transaction-table-row-date").attr("data-date");
						
						if (DEBUG){
							console.log("rowDate: " + rowDate);
							console.log("data.transactionDate: " + data.transactionDate);
						}
						
						adjacentRow = $(this);

						if (DEBUG){
							console.log("rowDate before?: " + moment(rowDate).isBefore(data.transactionDate));
							console.log("rowDate after?: " + moment(rowDate).isAfter(data.transactionDate));
							console.log("rowDate same date?: " + moment(rowDate).isSame(data.transactionDate, 'day'));
						}

						if (moment(rowDate).isAfter(data.transactionDate))
							return false;
					});

					/*
						Weird bug happening here - the first transaction of the day is always added in the second-to-last
						position rather than the first one. I need to observe this a little more.

						What seems to be happening is that if the most recently logged transaction isn't today, all 
						transactions logged today will be put right before it. So if the last logged transaction was the 8th
						and I add three on the 9th, they will all be put in this order:

							1. 8th 
							2. 9th
							3. 9th
							4. 9th
							5. 8th contd...

						... with all of the new transactions being placed after the most recent date that isn't today.


						I think I've solved it with adding the second check here, checking if the adjacentRowDataDate is
						also before the added transaction's date. That seems to work. I'm wondering if this will introduce
						further problems where a transaction might be logged a year and a day after the current date
						or something like that

					*/

					var adjacentRowDataDate = $(adjacentRow).find(".transaction-table-row-date").attr("data-date");

					if (moment(adjacentRowDataDate).isSame(data.transactionDate, 'day')
						|| moment(adjacentRowDataDate).isBefore(data.transactionDate, 'day'))
						var resultRow = $(data.transactionHtml).insertBefore(adjacentRow);
					else
						var resultRow = $(data.transactionHtml).insertAfter(adjacentRow);
				}

				$("#transaction-form").trigger("reset");
				$("#date-string").datepicker().data('datepicker').selectDate(new Date());
				$("#money-total").html(data.current_funds);

				redrawCharts();
				bindDeleteButtonEvents();
			}
		});
	});

	//initialize transaction form datepicker
	//again - I really don't like this id name
	$("#date-string").datepicker({
		maxDate: new Date(),
		onSelect: function(formattedDate, date, inst) {
			console.log("onSelect registered on #date-string: ");
			console.log("formattedDate: " + formattedDate);
			console.log("date: " + date);
			console.log("inst: " + inst);
		}
	});

	$("#date-range").datepicker({
		maxDate: new Date(),
		onSelect: function(formattedDate, date, inst) {
			if (DEBUG){
					console.log("onSelect registered on #date-range");
					console.log("date.length: " + date.length);
					console.log("inst._prevOnSelectValue: " + inst._prevOnSelectValue);
					console.log("formattedDate: " + formattedDate);
			}

			if (date.length > 1){
			/*
				below was previous code that worked, the second part of the logic check makes sure 
				the currently selected date isn't the same as the previous one, preventing a double
				load when the page loads and datepicker values are manually selected.

				Now it's not working. inst._prevOnSelectValue is always equal to formattedDate.

				Why is this?

				Actually, did this ever work? the idea is sound but I'm not sure if the implementation
				works.

			*/
			//if (date.length > 1 && inst._prevOnSelectValue != formattedDate){


				$("#transaction-table").remove();
				$("#table-wrapper").append(load_spinner_html);

				var allBoolean = false;
				var dateRangeData = $("#date-range").datepicker().data('datepicker');

				// this will never be true as you can't directly compare date objects.
				// moments.js will allow me to do this.
				if (date[0] == dateRangeData.minDate && date[1] == dateRangeData.maxDate)
					allBoolean = true;

				console.log("2 dates selected: " + date);
				$.ajax({
					url: "/",
					type: "GET",
					data: {
						all_boolean: allBoolean,
						date_range_start: date[0].toISOString(),
						date_range_end: date[1].toISOString()
					},
					success: function(data){
						console.log(data.date_range_start);
						console.log(data.date_range_end);
						$("#load-spinner").remove();
						$("#table-wrapper").append(data.table_html);

						$(".trends-header-range").html($("#date-range").val());

						if (data.all_boolean){
							console.log("all_boolean is set");
							if (!$("#data-range-all").hasClass("all-selected"))
								$("#data-range-all").addClass("all-selected");
						} else {
							console.log("all_boolean is not set.");
							$("#data-range-all").removeClass("all-selected");
						}

						redrawCharts()
						bindDeleteButtonEvents();

						//hide the global calendar
						// note that this should be fadeOut rather than toggle, or else triggered selection
						// events on this datepicker will cause the chart to appear (opposite of desired functionality)
						$("#global-calendar-container").fadeOut("fast");
					}
				});
			}
		}
	});

	$("#id_password_repeat").on("blur", function(){
		// check to see if passwords match. very basic warning now, return to this later
		if ($(this).val() == $("#id_password").val()){
			$(".budget-password").css("box-shadow", "inset 0px 0px 8px rgba(0,255,0,0.5)");
			$(".budget-password").css("background", "rgba(0,255,0,0.15)");
		} else {
			$(".budget-password").css("box-shadow", "inset 0px 0px 8px rgba(255,0,0,0.5)");
			$(".budget-password").css("background", "rgba(255,0,0,0.15)");
		}
	});
});
