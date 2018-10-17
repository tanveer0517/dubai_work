// My Account Form Fiel Upload Fields Validation

$(document).ready(function() {

    var emirates_id_card = ''
    var passport_and_poa = ''
    var vat_num = ''
    var visa_and_poa = ''
    var operating_address_uae = ''
    var trade_license = ''

    var file_list = [];
    //Check if file exist on the list
    //If file is already exist return true else it will add the file in list and return false
    var $upload_files_inputs = $('#Uploaded_Document input:file');
    function check_file_exist(file_name){
        if (file_list.indexOf(file_name) === -1) {
            file_list = []
            for (i=0;i<$upload_files_inputs.length;i++) {
                if($upload_files_inputs[i].files.length){
                    file_list.push($upload_files_inputs[i].files[0].name)
                }
            }
            return false;
        } else {
          return true;
        }
    }
    //Get all the input file type elements from the upload document form;
    //If file already exist alert user and make input value empty.
    $upload_files_inputs.change(function(e){
        var $el = $(this);
        if(!$el[0].files.length || _.isEmpty($el.val())){
            return;
        }
        var name = $el[0].files[0].name;
        if(check_file_exist(name)){
            alert(name + " alredy exist.")
            $el.val('')
        }
    });
});
