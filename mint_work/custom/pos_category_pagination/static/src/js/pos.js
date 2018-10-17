odoo.define('pos_category_pagination.pos_product_category', function(require) {
    "use strict";
    var core = require('web.core');
    var pos_screen = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var QWeb = core.qweb;
    pos_screen.ProductCategoriesWidget.include({
        init: function(parent, options) {
            var self = this;
            //Intialize counter for category pagination
            this.previous_start = -1
            this.previous_end = -1
            this.current_start = 0
            this.current_end = 0
            this.next_start = 0
            this.next_end = 0
            this._super(parent, options);
            this.maincategories = this.subcategories;
            this.parent_cat_list = [];
            this.switch_category_handler = function(event) {
                var allow_push = false;
                var categ_id = this.dataset.categoryId
                if (this.dataset.categoryId) {

                    var pre_st = self.previous_start;
                    var pre_en = self.previous_end;
                    var curr_st = self.current_start;
                    var curr_en = self.currrent_end;
                    var next_st = self.next_start;
                    var next_en = self.next_end;
                    if (self.subcategories.length > 0) {
                        self.previous_end = -1;
                        self.current_end= 0;
                        self.maincategories = self.subcategories;
                        allow_push = true;
                    }
                    var cat = self.pos.db.get_category_by_id(Number(this.dataset.categoryId));
                    //Reset parent_cat_list upto selected category
                    if (cat && self.parent_cat_list.length > 0) {
                        var updated_cat_list = self.parent_cat_list.slice();
                        for (var i = self.parent_cat_list.length - 1; i >= 0; i--) {
                            var get_cat = _.find(self.parent_cat_list[i].categories, function(c) {
                                return c.id == cat.id;
                            });
                            if (get_cat) {
                                for (var j = i; j < (self.parent_cat_list.length - 1) ; j++) {
                                    updated_cat_list.pop();
                                }
                                //Once more pop for main parent category
                                if (cat.parent_id == false && i == 0 && self.subcategories.length == 0 && updated_cat_list.length > 1) {
                                    updated_cat_list.pop();
                                }
                            }
                        }
                        self.parent_cat_list = updated_cat_list;

                    }
                    /*if (cat && cat.parent_id==false && self.parent_cat_list.length==1){
                        self.subcategories = self.parent_cat_list[0].categories;
                        self.parent_cat_list = [];
                    }*/
                    //Set category in parent tab
                    if (allow_push && this.dataset.categoryId && self.maincategories.length > 0 && self.maincategories[0].parent_id[0] == cat.parent_id[0]) {
                        self.parent_cat_list.push({
                            'sequence': self.parent_cat_list.length + 1,
                            'categories': self.maincategories,
                            'previous_start': pre_st,//-1,
                            'previous_end': pre_en,//-1,
                            'current_start': curr_st,//0,
                            'current_end': curr_en,//0,
                            'next_start': next_st,//0,
                            'next_end': next_en,//0
                        })
                        self.cal_page_para_category(true, self.parent_cat_list.length - 1);

                    }
                } else {
                    self.parent_cat_list = [];
                }
                self.set_category(cat);
                self.renderElement();
                var categ_to_active = []
                _.each(self.parent_cat_list, function(p_cat){
                    var get_category = _.find(p_cat.categories, function(c) {
                        return c.id == categ_id;
                    });
                    if(get_category){
                        categ_to_active.push(get_category.id)
                        if(get_category.parent_id){
                            categ_to_active.push(get_category.parent_id[0])
                        }
                    }
                })
                if(categ_to_active.length){
                    var cat_buttons = self.gui.chrome.$el.find('.category-button')
                    _.each(cat_buttons, function(ca){
                        var dom_categ_id = $(ca).data('category-id')
                        if(dom_categ_id){
                            if(_.contains(categ_to_active, dom_categ_id)){
                                $(ca).addClass('active_category')
                            }else{
                                $(ca).removeClass('active_category')
                            }
                        }
                    })
                }

            };

        },
        cal_page_para_category: function(new_rec=false, index) {
            var self = this;
            var curr_cat_step = self.parent_cat_list[index];
            var cat_length = curr_cat_step.categories.length;
            if (new_rec || (cat_length > 0 && cat_length > self.pos.config.default_show_no_of_category)) {
                if (curr_cat_step.previous_end < 0 && curr_cat_step.current_end == 0) {
                    curr_cat_step.current_start = 0;
                    curr_cat_step.current_end = cat_length > self.pos.config.default_show_no_of_category ? this.pos.config.default_show_no_of_category : cat_length;
                    curr_cat_step.next_start = cat_length > curr_cat_step.current_end ? curr_cat_step.current_end : cat_length;
                    var nextprepare = curr_cat_step.current_end + self.pos.config.default_show_no_of_category;
                    curr_cat_step.next_end = cat_length > nextprepare ? nextprepare : cat_length;
                    curr_cat_step.previous = false;
                } else {
                    var cnt = curr_cat_step.previous_end;
                    if (curr_cat_step.previous_end < 0) {
                        cnt = 0;
                    }
                    curr_cat_step.current_start = cat_length > cnt ? cnt : cat_length;
                    var nextprepare = curr_cat_step.current_start + self.pos.config.default_show_no_of_category;
                    curr_cat_step.current_end = cat_length > nextprepare ? nextprepare : cat_length;
                    if (cat_length > nextprepare) {
                        curr_cat_step.next_start = curr_cat_step.current_end;
                        var next_prepare = curr_cat_step.next_start + self.pos.config.default_show_no_of_category
                        curr_cat_step.next_end = cat_length > next_prepare ? next_prepare : cat_length;
                    }
                }
            } else {
                curr_cat_step.current_start = 0;
                curr_cat_step.current_end = curr_cat_step.categories.length;
            }
            self.parent_cat_list[index] = curr_cat_step;
        },
        // Action steps for parent-child category tree
        cal_action_cat_steps: function(btn, step_action) {
            var self = this;
            var subcat_length = this.subcategories.length;
            if (step_action == 'next') {
                self.previous_start = self.current_start;
                self.previous_end = self.current_end;
                self.current_start = self.next_start;
                self.current_end = self.next_end;
                self.next_start = subcat_length > self.next_end ? self.next_end : subcat_length;
                var prepare_next = self.next_start + this.pos.config.default_show_no_of_category;
                self.next_end = subcat_length > prepare_next ? prepare_next : subcat_length;
            } else if (step_action == 'previous') {
                var previous_start = self.previous_start;
                var previous_end = self.previous_end;
                self.next_start = self.current_start;
                self.next_end = self.current_end;
                self.current_start = previous_start;
                self.current_end = previous_end;

                self.previous_start = subcat_length > (self.current_start - this.pos.config.default_show_no_of_category) ? self.current_start - this.pos.config.default_show_no_of_category : -1;
                self.previous_end = subcat_length > self.current_start ? self.current_start : subcat_length;
            }
            this.renderElement();
        },
        cal_action_display_button_main_category: function(btn, display_action) {
            if (btn && btn.length > 0) {
                if (display_action) {
                    btn[0].style.display = 'inline-block';
                } else {
                    btn[0].style.display = 'none';
                }
            }
        },
        display_name: function(categ) {
            return categ.name.length > 20 ? categ.name.substr(0, 20) + '...' : categ.name;
        },
        action_display_button: function(btn_class, display_action) {
            if ($(btn_class).length > 0) {
                if (display_action) {
                    $(btn_class).show();
                } else {
                    $(btn_class).hide();
                }
            }
        },
        //Take step (Next/Previous) for subcategories
        action_category_steps: function(btn, step_action) {
            var self = this;
            var subcat_length = this.subcategories.length;
            if (step_action == 'next') {
                self.previous_start = self.current_start;
                self.previous_end = self.current_end;
                self.current_start = self.next_start;
                self.current_end = self.next_end;
                self.next_start = subcat_length > self.next_end ? self.next_end : subcat_length;
                var prepare_next = self.next_start + this.pos.config.default_show_no_of_category;
                self.next_end = subcat_length > prepare_next ? prepare_next : subcat_length;
                if (self.next_end == self.current_end) {
                    self.next = false;
                }
            } else if (step_action == 'previous') {
                var previous_start = self.previous_start;
                var previous_end = self.previous_end;
                self.next_start = self.current_start;
                self.next_end = self.current_end;
                self.current_start = previous_start;
                self.current_end = previous_end;

                self.previous_start = subcat_length > (self.current_start - this.pos.config.default_show_no_of_category) ? self.current_start - this.pos.config.default_show_no_of_category : -1;
                self.previous_end = subcat_length > self.current_start ? self.current_start : subcat_length;
            }
            this.renderElement();
        },
        parent_child_category_render: function() {
            // Main parent-child category
            var self = this;
            var withpics = this.pos.config.iface_display_categ_images;
            var main_cats = this.el.querySelector('.main-cat-list');
            if (main_cats) {
                main_cats.innerHTML = '';
                for (var k = 0; k < this.parent_cat_list.length; k++) {
                    var curr_parent_cat = this.parent_cat_list[k];
                    var sequence = this.parent_cat_list[k].sequence;
                    var main_cat_html = QWeb.render('main_cat_list', {
                        widget: this,
                        sequence: sequence,
                    });
                    var el_cat_node = document.createElement('div');
                    el_cat_node.innerHTML = main_cat_html;
                    el_cat_node = el_cat_node.childNodes[1];
                    var main_list_container = el_cat_node.querySelector('.maincategory-list');
                    // Previous Button
                    if (main_list_container && curr_parent_cat.categories.length > this.pos.config.default_show_no_of_category) {
                        var select_template = !withpics ? 'CategorySimplePreviousButton' : 'CategoryPreviousButton';

                        var category_previous_html = QWeb.render(this.pos.config.is_category_button ? (curr_parent_cat && curr_parent_cat.categories.length > 0 && curr_parent_cat.categories[0].parent_id ? 'CatSubPreviousBtn' : select_template) : select_template, {
                            widget: this,
                            sequence: sequence,
                        });
                        $($(main_list_container)[0]).prepend(category_previous_html);
                    }
                    self.main_parent_calculate_pagination_para(k);
                    // Update current category list
                    var curr_parent_cat = this.parent_cat_list[k];

                    if (main_list_container) {
                        if (!withpics) {
                            main_list_container.classList.add('simple');
                            main_list_container.classList.add('maincategory-list-btns');
                        } else {
                            main_list_container.classList.remove('simple');
                            main_list_container.classList.remove('maincategory-list-btns');
                        }
                        for (var i = curr_parent_cat.current_start, len = curr_parent_cat.current_end; i < len; i++) {
                            main_list_container.appendChild(this.render_category(curr_parent_cat.categories[i], withpics));
                        }
                    }
                    // Next Button
                    if (main_list_container && curr_parent_cat.categories.length > this.pos.config.default_show_no_of_category) {
                        var select_template = !withpics ? 'CategorySimpleNextButton' : 'CategoryNextButton';
                        var category_next_html = QWeb.render(this.pos.config.is_category_button ? (curr_parent_cat && curr_parent_cat.categories.length > 0 && curr_parent_cat.categories[0].parent_id ? 'CatSubNextBtn' : select_template) : select_template, {
                            widget: this,
                            sequence: sequence,
                        });
                        $($(main_list_container)[0]).append(category_next_html);
                    }
                    // Add item in DOM
                    main_cats.appendChild(el_cat_node);
                    // Next-previous button click events
                    // Next Buttons
                    var next_pagination_button = $('#cat_next_' + sequence);
                    var k_ind = k;
                    if ($('#cat_next_' + sequence)) {
                        $('#cat_next_' + sequence).on('click', function(event) {
                            self.action_maincategory_steps(event, 'next');
                        });
                    }
                    // Previous Buttons
                    var prev_pagination_button = $('#cat_previous_' + sequence);
                    if ($('#cat_previous_' + sequence)) {
                        $('#cat_previous_' + sequence).on('click', (function(event) {
                            self.action_maincategory_steps(event, 'previous');
                        }));
                    }
                    //Hide & Show pagination button
                    curr_parent_cat.previous = curr_parent_cat.previous_start >= 0 && curr_parent_cat.previous_end >= 0 ? true : false;
                    var pre_btn = $('#cat_previous_' + sequence); //el_cat_node.querySelector('.js-category-previous-'+sequence);
                    if (pre_btn) {
                        self.cal_action_display_button_main_category(pre_btn, curr_parent_cat.previous ? true : false);
                    }
                    curr_parent_cat.next = this.current_end == curr_parent_cat.categories.length ? false : true;
                    var next_btn = $('#cat_next_' + sequence); //el_cat_node.querySelector('.js-category-next-'+sequence);
                    if (next_btn) {
                        self.cal_action_display_button_main_category(next_btn, curr_parent_cat.next ? true : false);
                        // Check Empty categories
                        curr_parent_cat.next = curr_parent_cat.categories.length == curr_parent_cat.current_end ? false : true;
                        self.cal_action_display_button_main_category(next_btn, curr_parent_cat.next ? true : false);
                    }
                    // Bind category switcher with all category
                    var buttons = $('.js-category-switch');
                    for (var i = 0; i < buttons.length; i++) {
                        buttons[i].addEventListener('click', this.switch_category_handler);
                    }
                    self.parent_cat_list[k] = curr_parent_cat;

                }
               
            }
 setTimeout(function(){ 
                $('.category-list, .maincategory-list').css({'width': $('.rightpane').width(), 'display': 'flex'}); 
            }, 0);
        },
        //Take step (Next/Previous) for maincategories
        action_maincategory_steps: function(event, step_action) {
            var self = this;
            if ($('#' + event.currentTarget.id).length > 0) {
                var cat_seq = $('#' + event.currentTarget.id)[0].dataset.catIndex;
                for (var p = 0; p < self.parent_cat_list.length; p++) {
                    if (self.parent_cat_list[p].sequence == cat_seq) {
                        var cat_index = p;
                        var curr_parent_cat = self.parent_cat_list[p];
                        var cat_length = curr_parent_cat.categories.length;
                        var curr_parent_cat = self.parent_cat_list[cat_index];
                        if (step_action == 'next') {
                            curr_parent_cat.previous_start = curr_parent_cat.current_start;
                            curr_parent_cat.previous_end = curr_parent_cat.current_end;
                            curr_parent_cat.current_start = curr_parent_cat.next_start;
                            curr_parent_cat.current_end = curr_parent_cat.next_end;
                            curr_parent_cat.next_start = cat_length > curr_parent_cat.next_end ? curr_parent_cat.next_end : cat_length;
                            var prepare_next = curr_parent_cat.next_start + this.pos.config.default_show_no_of_category;
                            curr_parent_cat.next_end = cat_length > prepare_next ? prepare_next : cat_length;
                            if (curr_parent_cat.next_end == curr_parent_cat.current_end) {
                                curr_parent_cat.next = false;
                            }
                        } else if (step_action == 'previous') {
                            var previous_start = curr_parent_cat.previous_start;
                            var previous_end = curr_parent_cat.previous_end;
                            curr_parent_cat.next_start = curr_parent_cat.current_start;
                            curr_parent_cat.next_end = curr_parent_cat.current_end;
                            curr_parent_cat.current_start = previous_start;
                            curr_parent_cat.current_end = previous_end;

                            curr_parent_cat.previous_start = cat_length > (curr_parent_cat.current_start - this.pos.config.default_show_no_of_category) ? curr_parent_cat.current_start - this.pos.config.default_show_no_of_category : -1;
                            curr_parent_cat.previous_end = cat_length > curr_parent_cat.current_start ? curr_parent_cat.current_start : cat_length;
                        }
                        self.parent_cat_list[cat_index] = curr_parent_cat;
                        self.renderElement();
                    }
                }
            }

        },
        // Calculate pagination parameters for maincategories
        main_parent_calculate_pagination_para: function(cat_index) {
            var self = this;
            var curr_parent_cat = self.parent_cat_list[cat_index];
            var cat_length = curr_parent_cat.categories.length;
            if (cat_length > 0 && cat_length > this.pos.config.default_show_no_of_category) {
                if (curr_parent_cat.previous_end < 0 && curr_parent_cat.current_end == 0) {
                    curr_parent_cat.current_start = 0;
                    curr_parent_cat.current_end = cat_length > this.pos.config.default_show_no_of_category ? this.pos.config.default_show_no_of_category : cat_length;
                    curr_parent_cat.next_start = cat_length > curr_parent_cat.current_end ? curr_parent_cat.current_end : cat_length;
                    var nextprepare = curr_parent_cat.current_end + this.pos.config.default_show_no_of_category;
                    curr_parent_cat.next_end = cat_length > nextprepare ? nextprepare : cat_length;
                    curr_parent_cat.previous = false;
                } else {
                    var cnt = curr_parent_cat.previous_end;
                    if (curr_parent_cat.previous_end < 0) {
                        cnt = 0;
                    }
                    curr_parent_cat.current_start = cat_length > cnt ? cnt : cat_length;
                    var nextprepare = curr_parent_cat.current_start + this.pos.config.default_show_no_of_category;
                    curr_parent_cat.current_end = cat_length > nextprepare ? nextprepare : cat_length;
                    if (cat_length > nextprepare) {
                        curr_parent_cat.next_start = curr_parent_cat.current_end;
                        var next_prepare = curr_parent_cat.next_start + this.pos.config.default_show_no_of_category
                        curr_parent_cat.next_end = cat_length > next_prepare ? next_prepare : cat_length;
                    }
                }
            } else {
                curr_parent_cat.current_start = 0;
                curr_parent_cat.current_end = curr_parent_cat.categories.length;
            }
            this.parent_cat_list[cat_index] = curr_parent_cat
        },
        // Calculate pagination parameters
        calculate_pagination_para: function() {
            var self = this;
            var subcat_length = this.subcategories.length;
            if (subcat_length > 0 && subcat_length > this.pos.config.default_show_no_of_category) {
                if (this.previous_end < 0 && this.current_end == 0) {
                    this.current_start = 0;
                    this.current_end = subcat_length > this.pos.config.default_show_no_of_category ? this.pos.config.default_show_no_of_category : subcat_length;
                    this.next_start = subcat_length > this.current_end ? this.current_end : subcat_length;
                    var nextprepare = this.current_end + this.pos.config.default_show_no_of_category;
                    this.next_end = subcat_length > nextprepare ? nextprepare : subcat_length;
                    this.previous = false;
                } else {
                    var cnt = this.previous_end;
                    if (this.previous_end < 0) {
                        cnt = 0;
                    }
                    this.current_start = subcat_length > cnt ? cnt : subcat_length;
                    var nextprepare = this.current_start + this.pos.config.default_show_no_of_category;
                    this.current_end = subcat_length > nextprepare ? nextprepare : subcat_length;
                    if (subcat_length > nextprepare) {
                        this.next_start = this.current_end;
                        var next_prepare = this.next_start + this.pos.config.default_show_no_of_category
                        this.next_end = subcat_length > next_prepare ? next_prepare : subcat_length;
                    }
                }
            } else {
                this.current_start = 0;
                this.current_end = this.subcategories.length;
            }
        },
        renderElement: function() {
            var self = this;
            var el_str = QWeb.render(this.template, {
                widget: this
            });
            var el_node = document.createElement('div');
            el_node.innerHTML = el_str;
            el_node = el_node.childNodes[1];

            if (this.el && this.el.parentNode) {
                this.el.parentNode.replaceChild(el_node, this.el);
            }

            this.el = el_node;

            var withpics = this.pos.config.iface_display_categ_images;

            var list_container = el_node.querySelector('.category-list');

            //Start pagination calculation

            if ($('.category-list').length > 0 && this.subcategories.length > this.pos.config.default_show_no_of_category) {
                var select_template = !withpics ? 'CategorySimplePreviousButton' : 'CategoryPreviousButton';
                var category_previous_html = QWeb.render(this.pos.config.is_category_button ? (this.subcategories && this.subcategories[0].parent_id ? 'CatSubPreviousBtn' : select_template) : select_template, {
                    widget: this,
                });
                $($('.category-list')[0]).prepend(category_previous_html);
            }
            this.calculate_pagination_para();
            if (list_container) {
                if (!withpics) {
                    list_container.classList.add('simple');
                } else {
                    list_container.classList.remove('simple');
                }
                for (var i = this.current_start, len = this.current_end; i < len; i++) {
                    list_container.appendChild(this.render_category(this.subcategories[i], withpics));
                }
                if ($('.category-list').length > 0 && this.subcategories.length > this.pos.config.default_show_no_of_category) {
                    var select_template = !withpics ? 'CategorySimpleNextButton' : 'CategoryNextButton';
                    var category_next_html = QWeb.render(this.pos.config.is_category_button ? (this.subcategories && this.subcategories[0].parent_id ? 'CatSubNextBtn' : select_template) : select_template, {
                        widget: this,
                    });
                    $($('.category-list')[0]).append(category_next_html);
                }
            }

            var buttons = el_node.querySelectorAll('.js-category-switch');
            for (var i = 0; i < buttons.length; i++) {
                buttons[i].addEventListener('click', this.switch_category_handler);
            }
            // Next Buttons
            var next_pagination_button = el_node.querySelectorAll('.js-category-next');
            if (next_pagination_button.length > 0) {
                next_pagination_button[0].addEventListener('click', (function() {
                    this.action_category_steps(next_pagination_button[0], 'next');
                }.bind(this)));
            }
            // Previous Buttons
            var prev_pagination_button = el_node.querySelectorAll('.js-category-previous');
            if (prev_pagination_button.length > 0) {
                prev_pagination_button[0].addEventListener('click', (function() {
                    this.action_category_steps(prev_pagination_button[0], 'previous');
                }.bind(this)));
            }
            //Hide & Show pagination button
            this.previous = this.previous_start >= 0 && this.previous_end >= 0 ? true : false;
            this.action_display_button('.js-category-previous', this.previous ? true : false);
            this.next = this.current_end == this.subcategories.length ? false : true;
            this.action_display_button('.js-category-next', this.next ? true : false);
            // Parent-child category concept implement
            this.parent_child_category_render();
            var products = this.pos.db.get_product_by_category(this.category.id);
            this.product_list_widget.set_product_list(products); // FIXME: this should be moved elsewhere ...

            this.el.querySelector('.searchbox input').addEventListener('keypress', this.search_handler);

            this.el.querySelector('.searchbox input').addEventListener('keydown', this.search_handler);

            this.el.querySelector('.search-clear').addEventListener('click', this.clear_search_handler);

            if (this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard) {
                this.chrome.widget.keyboard.connect($(this.el.querySelector('.searchbox input')));
            }
           
        },

        // Subcategory show button only
        render_category: function(category, with_image) {

            var cached = this.category_cache.get_node(category.id);
            if (!cached) {
                if (with_image) {
                    var image_url = this.get_image_url(category);
                    var category_html = QWeb.render(this.pos.config.is_category_button ? (category.parent_id ? 'subcategory_button' : 'CategoryButton') : 'CategoryButton', {
                        widget: this,
                        category: category,
                        image_url: this.get_image_url(category),
                    });
                    category_html = _.str.trim(category_html);
                    var category_node = document.createElement('div');
                    category_node.innerHTML = category_html;
                    category_node = category_node.childNodes[0];
                } else {
                    var category_html = QWeb.render(this.pos.config.is_category_button ? (category.parent_id ? 'subcategory_button' : 'CategorySimpleButton') : 'CategorySimpleButton', {
                        widget: this,
                        category: category,
                    });
                    category_html = _.str.trim(category_html);
                    var category_node = document.createElement('div');
                    category_node.innerHTML = category_html;
                    category_node = category_node.childNodes[0];
                }
                this.category_cache.cache_node(category.id, category_node);
                return category_node;
            }
             setTimeout(function(){ 
                $('.category-list, .maincategory-list').css({'width': $('.rightpane').width(), 'display': 'flex', 'overflow-x': 'scroll', 'overflow-y': 'hidden'}); 
            }, 0);
            return cached;
        },

    });
});
