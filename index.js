var filename = '';
var encoded = null;
var fileExt = null;

function readURL(input) {
  if (input.files && input.files[0]) {

    var reader = new FileReader();

    filename = input.files[0].name;
    fileExt = filename.split('.').pop();
    var onlyname = filename.replace(/\.[^/.]+$/, "");
    var finalName = onlyname + "_" + Date.now() + "." + fileExt;
    filename = finalName;

    reader.onload = function (e) {

      var srcData = e.target.result;
      var newImage = document.createElement('img');
      newImage.src = srcData;
      encoded = newImage.outerHTML;
      $('.image-upload-wrap').hide();

      $('.file-upload-image').attr('src', e.target.result);
      $('.file-upload-content').show();

      $('.image-title').html(input.files[0].name);
    };

    reader.readAsDataURL(input.files[0]);
  } else {
    removeUpload();
  }
}

function removeUpload() {
  $('.file-upload-input').replaceWith($('.file-upload-input').clone());
  $('.file-upload-content').hide();
  $('.image-upload-wrap').show();
}
$('.image-upload-wrap').bind('dragover', function () {
  $('.image-upload-wrap').addClass('image-dropping');
});
$('.image-upload-wrap').bind('dragleave', function () {
  $('.image-upload-wrap').removeClass('image-dropping');
});



function imageUpload() {

  last_index_quote = encoded.lastIndexOf("\"");
   console.log("file type", fileExt)
  if (fileExt == "jpg" || fileExt == "jpeg") {
    encodedStr = encoded.substring(33, last_index_quote);
  } else {
    encodedStr = encoded.substring(32, last_index_quote);
  }

  var apigClient = apigClientFactory.newClient({
  });
  var params = {
    item: filename,
    "Content-Type": "text/plain",
    "Accept": "img/png",
  };

  var body = {
    encodedStr
  };

  var additionalParams = {
    headers: {
      "Content-Type": "text/plain",
    }
  };

  apigClient.photosItemPut(params, encodedStr, additionalParams)
    .then(function (result) {
      removeUpload();
    }).catch(function (result) {
      console.log("Error:", result)
    });
}

var imageList = [];

function setUpImapges(imageList) {

  var node = document.getElementById("photo-divs");

  while (node.hasChildNodes()) {
    node.removeChild(node.lastChild);
}

  if(imageList[0] == "" ){
    var newDiv = '<p class ="noImages" id="noImages" >Sorry! there are no images for this search<p>'
    $(".photo-divs").append(newDiv);
  }else{
    imageList.forEach(function (url) {
    var newDiv = '<div class="responsive"><div class="gallery"><img class = "photo" src="'+url+'" alt="Cinque Terre" width="600" height="400"></div>'
    $(".photo-divs").append(newDiv);
    });
  }
}

function search(e){
    var keycode = (e.keyCode ? e.keyCode : e.which);
    if (keycode == '13') {
        var searchTerm = document.getElementById('searchbar').value;
        
         console.log(searchTerm);
         var apigClient = apigClientFactory.newClient({});
         var params = {};
         var body = {};

        var additionalParams = {
         queryParams: {
          q: searchTerm
        }
      };

    apigClient.searchGet(params, body, additionalParams)
    .then(function (result) {
      console.log("result",result)
      var imageList = result.data.split(" ");
      console.log("imageList",imageList)
      console.log("length of imageList",imageList.length)
      setUpImapges(imageList);
    }).catch(function (result) {
      var newDiv = '<p class ="noImages">Some error occured !!!<p>'
        $(".photo-divs").append(newDiv);
        console.log(result);
    });
        document.getElementById('searchbar').value = "";
    }
}