$(document).ready(function() {

   $('#planinfo').on('show.bs.modal', function (event) {
      var button = $(event.relatedTarget)
      var tmpl_id = button.data('tmpl_id')
      var modal = $(this)
      $(modal).find("li").remove();
      $.ajax({
         url : "/web/plan/description",
         data: {'id': tmpl_id},
         success : function(plan_description) {
            var plan_desc = JSON.parse(plan_description);
            for (var i=0 ; i < plan_desc.length; i++)
            {
               modal.find('.modal-body #searchListUl').append
               ('<li>'+plan_desc[i]+'</li>')
            }
         }
      });
   });

//   $(".dropdown-menu li a").click(function(){
//
//    $("#LangDisp").text($(this).text());
////    $("#LangDisp")[0].innerText = $(this).text();
//  });


// Instantiate the Bootstrap carousel
$('.multi-item-carousel').carousel({
  interval: false
});

// for every slide in carousel, copy the next slide's item in the slide.
// Do the same for the next, next item.
$('.multi-item-carousel .item').each(function(){
  var next = $(this).next();
  if (!next.length) {
    next = $(this).siblings(':first');
  }
  next.children(':first-child').clone().appendTo($(this));
  
  if (next.next().length>0) {
    next.next().children(':first-child').clone().appendTo($(this));
  } else {
  	$(this).siblings(':first').children(':first-child').clone().appendTo($(this));
  }
});
});
