(function(ns){

  ns.displayViz = function(groupid){
    $(".vizgroup").hide();
    $("#"+groupid).show();
  }

  $(document).ready(function(){
    ns.displayViz('all');
    ns.spectrum("metasColor", "metas", "#00C400");
    ns.spectrum("widgetColor", "widget", "#FFFFFF");
    ns.spectrum("cumulColor", "cumul", "#00C400");
    ns.setResponsive();
    ns.downloadParls("deputes");
    ns.downloadParls("senateurs");
  });

})(window.cnap = window.cnap || {});

