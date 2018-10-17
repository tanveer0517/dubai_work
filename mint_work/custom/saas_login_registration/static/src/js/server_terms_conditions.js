$(document).ready(function() {

   $('#server_term_condition').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget)
      var plan_id = button.data('plan_id')
      var modal = $(this)
//      $(modal).find("li").remove();
      $.ajax({
         url : "/get_server_term_conditions",
         data: {'id': plan_id},
         success : function(server_term_condition) {
            var server_term_condition = JSON.parse(server_term_condition);
           modal.find('.modal-body #terms_conditions').html(server_term_condition)
         }
      });
   });
});
