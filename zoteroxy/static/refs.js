const Cite = require('citation-js');

jQuery(document).ready(() => {
    jQuery.ajax({
        url: '/collection',
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
                $("<div>").addClass("alert alert-danger").text("Failed to retrieve collection items...")
            );
        },
    });
});