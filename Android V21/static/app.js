$(document).ready(function() {
    $('#ville').change(function() {
        var ville = $(this).val();
        $.ajax({
            url: '/get_medecins',
            method: 'GET',
            data: { ville: ville },
            success: function(data) {
                $('#medecin').empty();  // Vider la liste actuelle des médecins
                if (data.length > 0) {
                    $.each(data, function(index, medecin) {
                        $('#medecin').append('<option value="' + medecin.id + '">' + medecin.first_name + ' ' + medecin.last_name + ' - ' + medecin.specialite + '</option>');
                    });
                } else {
                    $('#medecin').append('<option value="">Aucun médecin disponible</option>');
                }
            },
            error: function() {
                console.log("Erreur lors de la récupération des médecins.");
                $('#medecin').append('<option value="">Erreur lors de la récupération</option>');
            }
        });
    });
});
