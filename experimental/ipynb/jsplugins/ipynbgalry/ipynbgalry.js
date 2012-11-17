// Javascript handler.
// This function takes the json object and the cell DOM element as inputs.
// It can perform modifications to the DOM element in order to display
// something, using the information stored in the JSON object.
var galry_handler = function (json, element)
{
    // DOM id
    var id = 'Galry-'+IPython.utils.uuid();
    
    // Create a DIV HTML object to insert in the cell.
    var toinsert = $("<div/>").attr('id',id).attr('style', "width: 200px; height: 200px; background-color: black; color: white; font-size: 18pt; padding: 10px;").html(json['test']);
    element.append(toinsert);
};

// Link the handler name to the javascript function which performs
// some actions to display the object.
IPython.json_handlers.register_handler('GalryPlotHandler', galry_handler);
