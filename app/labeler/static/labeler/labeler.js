// Label names
var labels = ['merchant', 'amount', 'sub_total', 'tax', 'date']

// Keeps track of the sequence in which words as selected
// Never resets
var select_counter = 0

// Messages and alerts
no_selection_msg = "You have not selected any words! Please, select at least one word before assignment."
is_assigned_msg = "One of selected words has already been assigned. Please revise your selection."
no_assigned_msg = "No assigned words for this metric. No changes will be made."
empty_save_msg = "Cannot save because you did not assign any labels. Please assign labels now."

// Colors
var wordbox_fill_color = 'lightgrey'
var wordbox_outline_color = '#aaa'
var wordbox_font_color = '#333'

// Size and margins
var receipt_width = receipt.width
var receipt_height = receipt.height
var margin = {top: 20, right: 10, bottom: 20, left: 10}

// Zoom mode
var zoom_mode = false

// Draw receipt
function draw_receipt() {
	// Remove existing receipt
	d3.select("svg").remove()

	// Create parent svg
	var scale = Math.min(($('#receipt-viz').width() - margin.left - margin.right) / 300, 2)
	var window_width = $('#receipt-viz').width()
	var window_height = $('#right-col').height()

	// Create svg canvas
	var svg = d3.select("#receipt-viz").append("svg")
		.attr("id", "receipt")
  	.attr("width", window_width)
	  .attr("height", Math.max(receipt_height*scale + margin.top + margin.bottom, window_height))
	
	// Add group container for all svg shapes
	var svg_g = svg.append("g")
		.attr("id", "receipt_g")
  	.attr("transform", "translate(" + margin.left + "," + margin.top + ")")

  // Define zoom behavior
	var zoom = d3.zoom()
		.scaleExtent([0.75, 2])
		.on('zoom', function() {
			svg_g.attr('transform', d3.event.transform)
		})

	// Only enable zoom if zoom mode is on
	if (zoom_mode) svg.call(zoom)

	// Add receipt paper (background)
	svg_g.append('rect')
		.attr('id', 'receipt_background')
	 	.attr('x', 0)
	 	.attr('y', 0)
	 	.attr('rx', 5)
	 	.attr('ry', 5)
	 	.attr('width', receipt_width*scale)
	 	.attr('height', receipt_height*scale)
	 	.style('stroke', 'black')
	 	.style('fill', 'white')

	// Group for receipt words
	svg_g_w = svg_g.append("g")
		.attr("id", "receipt_g_w")
	// Place word boxes with labels
	for (i=0; i<receipt.words.length; i++){
		var word_height = receipt.words[i]['height']*scale

		// Define colors
		fill_color = wordbox_fill_color
				
		// Add word rectangle
		svg_g_w.append('rect')
			.attr('id', 'wid_'+receipt.words[i]['id'])
			.attr('class', 'word')
			.attr('x', receipt.words[i]['x1']*scale)
			.attr('y', receipt.words[i]['y1']*scale)
			.attr('rx', 3)
			.attr('ry', 3)
			.attr('width', receipt.words[i]['width']*scale)
			.attr('height', word_height)
			.attr('data-toggle', "popover")
			.attr('data-trigger', "hover")
			.attr('title', "Id: "+ receipt.words[i]['id'])
			.attr('data-content', "Text: " + receipt.words[i]['text'])
		// Add word text
		svg_g_w.append('text')
			.attr('x', receipt.words[i]['x1']*scale)
			.attr('y', receipt.words[i]['y1']*scale + word_height*0.8)
			.attr('font-size', word_height*0.8)
			.text(receipt.words[i]['text'])
			.style('fill', wordbox_font_color)
			.attr('pointer-events', "none")
	}
	draw_assigned()
}

// Draw assigned labels
function draw_assigned() {
	// Remove existing highlights
	d3.select("#assigned_layer").remove()

	var scale = Math.min(($('#receipt-viz').width() - margin.left - margin.right) / 300, 2);

	// Get receipt svg and append to it
	var svg_g_a = d3.select("#receipt_g")
		.append("g")
			.attr("id", "assigned_layer")

	// Place selected word boxes with labels
	for (j=0; j<labels.length; j++){
		var lbl = labels[j]
		// Get an array of assigned words
		var assigned_words = objs_from_wids(assigned[lbl])
		for (i=0; i<assigned_words.length; i++) {
			var word_height = assigned_words[i]['height']*scale					
			// Add word rectangle
			svg_g_a.append('rect')
				.attr('class', 'assigned '+lbl )
				.attr('x', assigned_words[i]['x1']*scale)
				.attr('y', assigned_words[i]['y1']*scale)
				.attr('rx', 3)
				.attr('ry', 3)
				.attr('width', assigned_words[i]['width']*scale)
				.attr('height', word_height)
				.attr('pointer-events', 'none')
			// Text
			svg_g_a.append('text')
				.attr('class', 'assigned_label '+lbl)
				.attr('x', assigned_words[i]['x1']*scale)
				.attr('y', assigned_words[i]['y1']*scale - 3)
				.attr('font-size', receipt_width/20)
				.text(lbl)
				.attr('pointer-events', "none")
		}
	}
}

// Marks word as selected
function select(word) {
	$(word).addClass('selected')
	$(word).attr('data-seq', select_counter)
	select_counter++
}

// Deselect words
function deselect(word) {
	$(word).removeClass('selected')
	$(word).removeAttr('data-seq')
}

// Removes all selections on page
function deselectAll() {
	$('.word').removeClass('selected')
	$('.word').removeAttr('data-seq')
}

// Function to make array of selected words' ids in their selection sequence
function get_wids(selected_words) {
	var wids = []
	// Build array of objects
	for (i=0;i<selected_words.length;i++) {
		wids.push({
			'wid': selected_words[i].id.replace('wid_', ''),
			'seq': parseInt($(selected_words[i]).attr('data-seq').replace('seq_', ''))
		})
	}
	// Sort by sequence
	wids.sort(function(a, b) {
		return (a.seq > b.seq) ? 1 : ((b.seq > a.seq) ? -1 : 0)
	})
	// Return array of wids only
	return wids.map(function(a) {return parseInt(a.wid)})
}

// Builds an array of word objects given an array of their ids
function objs_from_wids(wids) {
	return receipt.words.filter(function(word) {
			return $.inArray(word.id, wids) > -1
		})
}

// Generates value string from an array of words
function build_value(wids, sep='') {
	var assigned_words = objs_from_wids(wids)
	var text_arr = assigned_words.map(function(a) {return a.text})
	return text_arr.join(sep)
}

// Checks if words has already been assigned
function is_assigned(selected_words) {
	assigned_flat = Object.keys(assigned)
		.reduce(function (r, k) {
			return r.concat(assigned[k]) 
		}, [])
	// Return true if one of selected words has been assigned earlier
	for (i=0;i<selected_words.length;i++) {
		if ($.inArray(selected_words[i], assigned_flat) > -1) return true
	}
	return false
}

// Toggle status badges
function update_status(lbl, status) {
	// Update status
	if (status=='ok') {
		$('#'+lbl+'_ok').show()
		$('#'+lbl+'_ng').hide()	
	} else {
		$('#'+lbl+'_ok').hide()
		$('#'+lbl+'_ng').show()
	}
	
}

// Attach event handlers
// Need to be reattached at every receipt redraw
function bindHandlers() {
	// Handle word clicks
	$('.word').on('click', function(event){
		if ($(this).hasClass('selected')) {
			deselect(this)
		} else {
			if (!event.ctrlKey && !event.shiftKey) {
				deselectAll()
			}
			select(this)
		}
	})
	// Click on white background
	$('#receipt_background').on('click', function(){
		deselectAll()
	})

	// Reenable bootstrap tooltips and popovers
	enableTooltipsPopovers()
}

// Enable bootstrap popovers and tooltips
function enableTooltipsPopovers() {
  $('[data-toggle="popover"]').popover()
  $('[data-toggle="tooltip"]').tooltip()
}

// Truncate missing/broken buttons' text
function shrinkBtns() {
	if ($('.assign').parent().width() < 320) {
		$('button.missing').text("Ms")
		$('button.broken').text("Br")
	} else {
		$('button.missing').text("Missing")
		$('button.broken').text("Broken")
	}
}

// Redraw receipt on window resize
$(window).resize(function() {
	draw_receipt()
	bindHandlers()
	shrinkBtns()
})

/*
-------------------------------------------------------
*/

$(document).ready(function(){
	
	// Render receipt
	draw_receipt()
	bindHandlers()
	shrinkBtns()

	// Assign button click
	$('.assign').on('click', function() {
		// Determine which label assigned
		var lbl = this.id.replace('assign_', '')
		// Get list of selected words
		var selected = $('.word.selected')
		// Display alert if selection empty or proceed
		if (selected.length == 0) {
			$('#simple_alert_msg').text(no_selection_msg)
			$('#simple_alert').modal('show')
		}
		// Warn if one of the words has been assigned
		else if (is_assigned(get_wids(selected))) {
			$('#simple_alert_msg').text(is_assigned_msg)
			$('#simple_alert').modal('show')
			deselectAll()
		}
		else {
			// Get ids of selected words
			var wids = get_wids(selected)
			// Update hidden input
			$('input[name='+lbl+'_selection]').attr('value', wids.join("|"))
			// Remove selection, change status
			deselectAll()
			update_status(lbl, 'ok')
			// Update displayed value
			var txt = ''
			if (lbl=='merchant') {
				txt = build_value(wids, ' ')
			} else {
				txt = build_value(wids, '')
			}
			$('#'+lbl+'_val').text(txt)
			// Keep track of assigned ids
			assigned[lbl] = wids
			// Highlight assigned words
			draw_assigned()
		}
	})

	// Missing button click
	$('.missing').on('click', function() {
		// Determine label
		var lbl = this.id.replace('missing_', '')
		// Update hidden input
		$('input[name='+lbl+'_selection]').attr('value', 'm')
		// Remove selection, change status
		deselectAll()
		update_status(lbl, 'ok')
		// Update displayed value
		$('#'+lbl+'_val').text('[Missing]')
		// Keep track of assigned ids
		assigned[lbl] = []
		// Highlight assigned words
		draw_assigned()
	})

	// Broken button click
	$('.broken').on('click', function() {
		// Determine label
		var lbl = this.id.replace('broken_', '')
		// Update hidden input
		$('input[name='+lbl+'_selection]').attr('value', 'b')
		// Remove selection, change status
		deselectAll()
		update_status(lbl, 'ok')
		// Update displayed value
		$('#'+lbl+'_val').text('[Broken]')
		// Keep track of assigned ids
		assigned[lbl] = []
		// Highlight assigned words
		draw_assigned()
	})

	// Undo button click
	$('.undo').on('click', function() {
		// Determine which label undone
		var lbl = this.id.replace('undo_', '')
		// Get list of assigned words
		var assigned_ids = assigned[lbl]
		// Display alert if selection empty or proceed
		if (assigned_ids.length == 0) {
			$('#simple_alert_msg').text(no_assigned_msg)
			$('#simple_alert').modal('show')
		}
		else {
			// Update hidden input
			$('input[name='+lbl+'_selection]').attr('value', '')
			// Remove selection, change status
			deselectAll()
			update_status(lbl, 'ng')
			// Update displayed value
			$('#'+lbl+'_val').text('')
			// Clear assigned ids
			assigned[lbl] = []
			// Dehighlight assigned words
			draw_assigned()
		}
	})

	// Highlight assigned word on table row hover
	$('.label_row').hover(
		function() {
			var lbl = this.id.replace('_row', '')
			$('.assigned.'+lbl).addClass('highlight')
			$('.assigned_label.'+lbl).addClass('highlight')
		},
		function() {
			var lbl = this.id.replace('_row', '')
			$('.assigned.'+lbl).removeClass('highlight')
			$('.assigned_label.'+lbl).removeClass('highlight')
		})

	// Validate form before submit
	$('#save_form').on('submit', function(event) {
		// Stop submission
		event.preventDefault()
		var inputs = $('.selection_input')
		// Count invalid inputs
		var valid_counter = 0
		for (i=0;i<inputs.length;i++) {
			var val = $(inputs[i]).val()
			if (val == 'm' || val == 'b' || parseInt(val) > 0 ) {
				valid_counter++
			} 
		}
		// Issue alerts or submit
		if (valid_counter == 0) {
			// Alert if no assignments
			$('#simple_alert_msg').text(empty_save_msg)
			$('#simple_alert').modal('show')
		} else if (valid_counter < inputs.length) {
			// Dismissable alert if not all words assigned
			$('#submit_alert').modal('show')
		} else {
			// Submit if all is ok
			$('#save_form')[0].submit()
		}
	})

	// Submit form from alert if alert was dismissed 
	$('#dismiss_submit').on('click', function() {
		$('#save_form')[0].submit()
		$('#submit_alert').modal('hide')
	})

	// Toggle zoom mode
	$('#zoom_toggle').on('click', function() {
		if ($(this).hasClass('active')) {
			$(this).removeClass('active')
			$(this).text("Zoom Off")
			zoom_mode = false
			draw_receipt()
			bindHandlers()
		} else {
			$(this).addClass('active')
			$(this).text("Zoom On")
			zoom_mode = true
			draw_receipt()
			bindHandlers()
		}
	})

	// Clean up alert modal upon closing
	$('#simple_alert').on('hidden.bs.modal', function (e) {
	  $('#simple_alert_msg').text("")
	})

})