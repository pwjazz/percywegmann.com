// Constants
var SCALE_FACTOR = 1.5;

// UI model
var scale = 1;
var chemicals = [];
var baseUrl = null;
var perCapita = false;
var chemical = "ALL";

// Information about original dimensions for zooming
var originalContentWidth = 960;
var originalMapWidth = 555;
var originalMapHeight = 351;

// Adjusts UI controls based on current scale
function adjustScale() {
	$("#content").width(originalContentWidth * scale);
	$("#hoverHelp").width(originalMapWidth * scale);
	$("#map").width(originalMapWidth * scale);
	$("#map").height(originalMapHeight * scale);
	$("#scalingGroup").attr("transform", "scale(" + scale + ")");
}

// Selects the current metric link
function selectCurrentMetric(current) {
	$("#viewSelectors a").removeClass("current");
	$(current).addClass("current");
}

// Initialize UI
$(document).ready(function() {
	// Initialize qtip tooltips for each county on map
	$("#map .county").each(function() {
		var county = $(this);
		county.attr("title", county.attr("inkscape:label")).qtip();
	});
	
	// Initialize handling for the 4 metric links
	$("#by_incidents").click(function() {
		selectCurrentMetric(this);
		updateMap("incidents", false);
	});
	$("#by_incidents_per_capita").click(function() {
		selectCurrentMetric(this);
		updateMap("incidents", true);
	});
	$("#by_pounds").click(function() {
		selectCurrentMetric(this);
		updateMap("poundsReleased", false);
	});
	$("#by_pounds_per_capita").click(function() {
		selectCurrentMetric(this);
		updateMap("poundsReleased", true);
	});
	
	// Zoom-in handling
	$("#enlarge").click(function() {
		if (scale == 1) {
			scale = 1.25;
		} else {
			scale = Math.pow(scale, SCALE_FACTOR)
		}
    	adjustScale();
    	return false;
	});
	
	// Zoom-out handling
	$("#reduce").click(function() {
		if (scale == 1) return;
		if (scale <= 1.3) {
			scale = 1;
		} else {
			scale = Math.pow(scale, 1/SCALE_FACTOR)
		}
    	adjustScale();
    	return false;
	});
	
	// Zoom to original handling
	$("#zoomOriginal").click(function() {
		if (scale == 1) return;
		scale = 1;
    	adjustScale();
    	return false;
	});
	
	// Process submission of chemical form (for filtering chemical)
	$("#chemicalForm").submit(function() {
		var input = $("#chemical");
		var chemical = input.val().toUpperCase();
		if (chemical == "" || chemicals.indexOf(chemical) >= 0) {
			$("#error").html("");
			updateMap(baseUrl, perCapita, chemical);
		} else {
			$("#error").html("Please select one of the listed chemicals");
		}
		return false;
	});
    
	initChemicals();
	updateMap("incidents");
});

// Initialize the list of chemicals
// If we were using a templating engine, we might just embed the JSON in the HTML instead of making a separate call
function initChemicals() {
	$.ajax({
		url: 'chemicals',
		cache: true,
		dataType: "json"
	}).done(function (json) {
		chemicals = json;
		
		// Set up auto-complete handling
		var input = $("#chemical");
		function showAutoComplete() {
			input.autocomplete("search", input.val().toUpperCase())
		}
		function acceptChange() {
			$("#chemicalForm").submit();
		}
		input
			.autocomplete({source: chemicals, minLength: 0})
			.click(showAutoComplete)
			.bind("autocompleteselect", function (event, ui) {
				// Do this later to make sure that field value has been updated before we submit
				setTimeout("$('#chemicalForm').submit()", 0);
			});
		$("#dropDownArrow").click(function() {
			input.val("");
			showAutoComplete();
			input.focus();
		});
		$("#showAll").click(function() {
			input.val("");
			$('#chemicalForm').submit();
		});
		input.change(acceptChange);
	});
}

// Update the map
function updateMap(_baseUrl, _perCapita, _chemical) {
	$("body").mask("Updating map ...");
	baseUrl = _baseUrl;
	if (_perCapita != null) {
		perCapita = _perCapita;
	}
	if (_chemical != null) {
		chemical = _chemical;
	}
	
	var url = baseUrl + "?"
	if (chemical) url = url + "chemical=" + encodeURIComponent(chemical);
	if (perCapita) {
		if (chemical) url = url + "&";
		url = url + "perCapita=true"
	}
	
	$.ajax({
		url: url,
		cache: true,
		dataType: "json"
	}).done(function (data) {
		$("body").unmask();
		
		// Set up an appropriate label for the current measure
		var label = "incidents";
		if (baseUrl == "poundsReleased") {
			label = "pounds";
		}
		if (perCapita) {
			label = label + "  / 1,000 res.";
		}
		
		// Update each of the 5 ranges in the legend
		for (var i=0; i<data.intervals.length; i++) {
			var text = ""
		    if (i == 0) {
		    	$("#range0").html("< " + data.intervals[i] + "<br/><span class='info'>" + label + "</span>");
		    }
			if (i == data.intervals.length - 1) {
		    	text = "> " + humanizeNumber(data.intervals[i]);
		    } else {
		    	text = humanizeNumber(data.intervals[i]) + " - " + humanizeNumber(data.intervals[i + 1]);
		    }
			text = text + "<br/><span class='info'>" + label + "</span>";
			$("#range" + (i+1)).html(text);
		}
		
		// Update each county
		$("#map .county").each(function() {
			var county = $(this);
			var countyData = data.totals[county.attr("id")];
			var interval = 0;
			var total = 0;
			if (countyData) {
				interval = countyData.interval;
				total = countyData.total;
			}
			county.attr("class", "county county" + interval);
			county.attr("title", county.attr("inkscape:label") + ": " + humanizeNumber(total) + " " + label);
		});
	});
}

// Makes numbers more readable
// Numbers under 1,000 are simly rounded to 2 decimal places
// Numbers between 1,000 and 1,000,000 are rounded to 0 decimal places and get commas
// Numbers from 1 mil + get converted into words
function humanizeNumber(number) {
	if (number < 1000) return Math.round(number * 100) / 100;
	if (number < 1000000) return Humanize.intcomma(Math.round(number));
	return Humanize.intword(Math.round(number))
}