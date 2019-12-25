$(document).ready(function(){
    cross_animationIn();
  setTimeout(function(){
    tick_animationIn();
  },1500)
  
});

function cross_animationIn(){
	$("#cross_circle")
	    .delay(100)
		  .velocity({strokeWidth: 30},200, "easeOutExpo")
			.velocity({strokeDasharray:1600,strokeDashoffset: 0},700, "easeInOutSine")
      //.delay(1500)
      //.velocity("reverse"); //Use this to run the animation in reverse essentially 'animating out'.

	$("#cross_p1")
	    .delay(100)
		  .velocity({ height: 376.964, width: 33.205 },300, "easeOutQuart")
      //.delay(1500)
      //.velocity("reverse");

			$("#cross_p2")
					.delay(100)
					.velocity({ height: 376.964, width: 33.205 },500, "easeOutQuart" )
      
          //.delay(1500)
          //.velocity("reverse");
}

function tick_animationIn(){
	$("#tick_circle")
	    .delay(100)
		  .velocity({strokeWidth: 30},200, "easeOutExpo")
			.velocity({strokeDasharray:1600,strokeDashoffset: 0},700, "easeInOutSine");

	$("#tick_p1")
	    .delay(100)
		  .velocity({ height: 137.999, width: 30 },300, "easeInExpo");

			$("#tick_p2")
					.delay(100)
					.velocity({ height: 259.334, width: 30 },500, "easeOutExpo" );
}
