const Cite = require('citation-js');

function showCollection(endpoint, $elem) {
    jQuery.ajax({
        url: `${endpoint}/collection`,
        method: 'GET',
        dataType: 'json',
        headers : {
            Accept: 'application/json'
        },
        success: (data) => {
            console.log(data);
            const cites = data.items.map((item) => new Cite(item.bibjson));
            jQuery("#refs").empty();
            cites.forEach((c) => {
                const html = c.format('bibliography', {
                      format: 'html',
                      template: 'apa',
                });
                jQuery("#refs").append(
                    jQuery.parseHTML(html)
                );
            });
        },
        error: () => {
            console.log("Error");
            jQuery("#refs").empty();
            jQuery("#refs").append(
                jQuery("<div>").addClass("alert alert-danger").text("Failed to retrieve collection items...")
            );
        },
    });
}

jQuery(document).ready(() => {
    const endpoint = jQuery("#refs").data('endpoint');
    showCollection(endpoint, this);
});
