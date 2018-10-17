// Registration Form Fields Validation

$(document).ready(function() {

//  Function to check Email Exist in the database or not
    $("#email").change(function() {
        var email = $("#registration_form_val").find("#email").val()
        var formData =  $( this ).serializeArray();
        console.log(formData)
        $.ajax({
            url: '/get_email_rec',
            dataType: 'json',
            data: formData,
            success: function(response) {
                console.log(response);
                if (response['error']){
                    $("#registration_form_val").find('#email_check').text(response['error']);
                }
                if (response['available']){
                    $("#registration_form_val").find('#email_check').text("");
                }
            },
            error: function() {
                console.log('error');
            }
        });
    });

//  Function to check Domain Exist in the database or not
    $("#domain").change(function() {
        var domain = $("#registration_form_val").find("#domain").val()
        var base_saas_domain = $("#registration_form_val").find("#base_saas_domain").val()
        var formData =  $( this ).serializeArray();
        formData.push({name: "base_saas_domain", value:base_saas_domain });
        console.log(formData)
        $.ajax({
            url: '/get_domain_rec',
            dataType: 'json',
            data: formData,
            success: function(response) {
                console.log(response);
                if (response['error']){
                    $("#registration_form_val").find('#domain_check').text(response['error']);
                }
                if (response['available']){
                    $("#registration_form_val").find('#domain_check').text("");
                }
            },
            error: function() {
                console.log('error');
            }
        });
    });

//  onchange method to get the country and state text value and set it in a
//  hidden field for use
    $(function() {
        var countryName = $( this ).find("#countries_phone1 option:selected").text()
        $("#registration_form_val").find("#country_name").val(countryName)
    });

    $("#countries_phone1").change(function() {
        var countryName = $("#registration_form_val").find("#countries_phone1 option:selected").text()
        $("#registration_form_val").find("#country_name").val(countryName)
    });

//    $(".bfh-states").change(function() {
//        var stateName = $("#registration_form_val").find(".bfh-states option:selected").text()
//        $("#registration_form_val").find("#state_name").val(stateName)
//    });

//  Keyup event when we type space in company name it will replace it with '_'
//  in domain field
    $(".one").keyup(function () {
        var a = $(".one").val();
        var c = (a).toLowerCase().replace(/[^ a-zA-Z0-9\d-]/g, "").replace(/ /g,"-");
        $(".two").val(c);
    });
    $(".two").keyup(function () {
        var a = $(".two").val();
        var c = (a).toLowerCase().replace(/[^ a-zA-Z0-9\d-]/g, "").replace(/ /g, "-");
        $(".two").val(c);
        if (c.startsWith("-")){
            var edited = c.replace(/^-|-$/g,'');
            $(".two").val(edited);
        }
        if (c.endsWith("-")){
            var edited = c.replace(/^-|-$/g,'');
            $(".two").val(edited);
        }
    });
    $("#landline_no").keyup(function () {
        var a = $("#landline_no").val();
        var c = (a).replace(/[^ 0-9\d-]/g, "").replace(/ /g,"-");
        $("#landline_no").val(c);
    });

//  Change event if the checkbox is not checked the button will be disabled
    $('.agree_terms').click(function () {
        //check if checkbox is checked
        if ($(this).is('checked')) {
            $('.submit').removeAttr('disabled'); //enable input
        } else {
            $('.submit').attr('disabled', true); //disable input
        }
    });

//  bootstrapValidator to validate the form elements
    $('#registration_form_val').bootstrapValidator({
        // To use feedback icons, ensure that you use Bootstrap v3.1.0 or later
        feedbackIcons: {
            valid: 'fa fa-check',
            invalid: 'fa fa-times',
            validating: 'fa fa-refresh'
        },
        fields:
        {
            full_name: {
                validators: {
                        stringLength: {
                        min: 3,
                    },
                        notEmpty: {
                        message: 'Please enter your Full Name'
                    }
                }
            },
            street1: {
                validators: {

                        notEmpty: {
                        message: 'Please enter your House No or Name'
                    }
                }
            },
            street2: {
                validators: {

                        notEmpty: {
                        message: 'Please enter your Locality or Street Name'
                    }
                }
            },
            city: {
                validators: {
                        stringLength: {
                        min: 3,
                    },
                        notEmpty: {
                        message: 'Please enter your City'
                    }
                }
            },
            contact_no: {
                validators: {
                        stringLength: {
                        min: 11,
                    },
                        notEmpty: {
                        message: 'Please enter your valid contact no'
                    }
                }
            },
            landline_no: {
                validators: {
                        stringLength: {
                        min: 13,
                    },
                        notEmpty: {
                        message: 'Please enter your valid Landline no'
                    }
                }
            },
            company_name: {
                validators: {
                     stringLength: {
                        min: 3,
                    },
                    notEmpty: {
                        message: 'Please enter your Company Name (length > 3)'
                    }
                }
            },
            base_saas_domain_name: {
                validators: {
                     stringLength: {
                        min: 3,
                    },
                    notEmpty: {
                        message: 'Please enter your Company Name (length > 3)'
                    }
                }
            },
            email: {
                validators: {
                    notEmpty: {
                        message: 'Please enter your Email Address'
                    },
                    emailAddress: {
                        message: 'Please enter a valid Email Address'
                    }
//                    remote: {
//                        message: 'The email is not available',
//                        url: '/get_email_rec',
//                        data: {
//                            type: 'email'
//                        },
//                        type: 'POST'
//                    }
                }
            },
            business_type: {
                validators: {
                    notEmpty: {
                        message: 'Please select your Business Type'
                    }
                }
            },
            bank_rec_id: {
                validators: {
                    notEmpty: {
                        message: 'Please select your Bank Name'
                    }
                }
            },
            account_num: {
                validators: {
                        stringLength: {
                        min: 12,
                        max: 16,
                    },
                        notEmpty: {
                        message: 'Please enter your Valid Bank Account Number'
                    }
                }
            },
            bank_iban: {
                validators: {
                        stringLength: {
                        min: 16,
                        max: 25,
                    },
                        notEmpty: {
                        message: 'Please enter your Valid Bank IBAN.'
                    }
                }
            },
//            multi_documents: {
//                validators: {
//                    file: {
//                        extension: 'docx,pdf',
//                        type: 'application/msword,application/pdf',
//                        maxSize: 2048 * 1024,
//                        message: 'The selected file is not valid. Only PDF and Docx files are allowed with max size 2mb'
//                    }
//                }
//            },
        }
        }).on('success.form.bv', function(e) {
            $('#success_message').slideDown({ opacity: "show" }, "slow") // Do something ...
            $('#registration_form_val').data('bootstrapValidator').resetForm();

            // Prevent form submission
            e.preventDefault();

            // Get the form instance
            var $form = $(e.target);

            // Get the BootstrapValidator instance
            var bv = $form.data('bootstrapValidator');

            // Use Ajax to submit form data
            $.post($form.attr('action'), $form.serialize(), function(result) {
                console.log(result);
            }, 'json');
    });
       $(window).on("scroll", function() {
    if($(window).scrollTop() > 50) {
        $(".navbar").addClass("custom_background");
    } else {
        //remove the background property so it comes transparent again (defined in your css)
       $(".navbar").removeClass("custom_background");
    }
    });

//    ======================================================================
//    =======Reference Code may be used Afterwards =========================
//    ======================================================================


//    $("#registration_form_val").submit(function(e) {
//        e.preventDefault();

//        var countryName = $( this ).find("#countries_phone1 option:selected").text()
//        var stateName = $(this).find(".bfh-states option:selected").text();
//
//        var formData =  $( this ).serializeArray();
//        formData.push({name: "country_name", value:countryName },
//        {name:"state_name", value: stateName});
//
//        This code is also working fine =======================
//        $.ajax({
//            url: '/process',
//            type: 'POST',
//            data: formData,
//            success: function(response) {
//                console.log(response);
//            },
//            error: function(error) {
//                console.log(error);
//            }
//        });
//
//        fetch('/registration', {
//            method: 'post',
//            body: JSON.stringify(formData)
//        });
//
//    });

//  validation for the file upload to upload specific file type and limit size
//    $('#multi_upload_docs').change(function(){
//           var fp = $("#multi_upload_docs");
//           var lg = fp[0].files.length; // get length
//           var items = fp[0].files;
//           var fileSize = 0;
//
//       if (lg > 0) {
//           for (var i = 0; i < lg; i++) {
//               fileSize = fileSize+items[i].size; // get file size
//           }
//           if(fileSize > 2097152) {
//                alert('File size must not be more than 2 MB');
//                $('#multi_upload_docs').val('');
//           }
//       }
//    });


//    $("#bank_name").change(function() {
//        var bank = $("#registration_form_val").find("#bank_name").val()
//        var formData =  $( this ).serializeArray();
//        $.ajax({
//            url: '/get_bank_rec',
//            dataType: 'json',
//            data: formData,
//            success: function(response) {
//                console.log(response);
//                if (response['error']){
//                    $("#registration_form_val").find('#bank_iban_missing').text(response['error']);
//                }
//                if (response['bank_iban']){
//                    $("#registration_form_val").find('#bank_iban').val(response['bank_iban']);
//                }
//            },
//            error: function() {
//                console.log('error');
//            }
//        });
//    });

});
