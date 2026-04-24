(function ($) {
  "use strict";

  $(function () {
    var header = $("header");
    $(window).scroll(function () {
      var scroll = $(window).scrollTop();

      if (scroll >= 130) {
        header.removeClass('start-style').addClass("scroll-on");
      } else {
        header.removeClass("scroll-on").addClass('start-style');
      }
    });

    var navMenu = document.getElementById('navbarMainMenu');
    if (navMenu) {
      navMenu.addEventListener('show.bs.collapse', function () {
        document.body.classList.add('menu-open');
      });
      navMenu.addEventListener('hide.bs.collapse', function () {
        document.body.classList.remove('menu-open');
      });

      document.addEventListener('click', function (e) {
        if (!document.body.classList.contains('menu-open')) return;
        var headerEl = document.querySelector('header');
        if (headerEl && !headerEl.contains(e.target)) {
          var bsCollapse = bootstrap.Collapse.getInstance(navMenu);
          if (bsCollapse) bsCollapse.hide();
        }
      });
    }


  });


})(jQuery);


var swiperIntegrations = new Swiper(".swiperIntegrations", {
  slidesPerView: 1.2,
  spaceBetween: 16,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  navigation: {
    nextEl: ".swiper-button-next-integrations",
    prevEl: ".swiper-button-prev-integrations",
  },
  breakpoints: {
    640: {
      slidesPerView: 1.3,
      spaceBetween: 8,
    },
    768: {
      slidesPerView: 1.2,
      spaceBetween: 20,
    },
    1024: {
      slidesPerView: 1.3,
      spaceBetween: 24,
    },
  },
});

var swiperSolutions = new Swiper(".swiperSolutions", {
  slidesPerView: 1.3,
  spaceBetween: 16,
  slidesOffsetBefore: 16,
  slidesOffsetAfter: 16,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  breakpoints: {
    640: {
      slidesPerView: 1.3,
      spaceBetween: 8,
    },
    768: {
      slidesPerView: 1.2,
      slidesOffsetBefore: 0,
      slidesOffsetAfter: 0,
      spaceBetween: 20,
    },
    1024: {
      slidesPerView: 3,
      slidesOffsetBefore: 0,
      slidesOffsetAfter: 0,
      spaceBetween: 24.5,
    },
  },
});

var swiperAlliance = new Swiper(".swiperAlliance", {
  slidesPerView: 1.3,
  slidesPerGroup: 1,
  spaceBetween: 16,
  slidesOffsetBefore: 16,
  slidesOffsetAfter: 16,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  breakpoints: {
    640: {
      slidesPerView: 1.3,
      slidesPerGroup: 1,
      spaceBetween: 8,
    },
    768: {
      slidesPerView: 1.2,
      slidesPerGroup: 1,
      slidesOffsetBefore: 0,
      slidesOffsetAfter: 0,
      spaceBetween: 20,
    },
    1024: {
      slidesPerView: 3,
      slidesPerGroup: 3,
      slidesOffsetBefore: 0,
      slidesOffsetAfter: 0,
      spaceBetween: 24,
    },
  },
});










const SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwuNZwxFXEdxVKuR7tw0-l9jAwoP08mJrVSfvttTi5ax4cMVN0YD-x5cDZWwR6Ff6y-Jg/exec";

$(document).ready(function () {

  function checkContactFormFields() {
    const $form = $('#form-contact');
    if ($form.length === 0) return;

    const firstname = $form.find('input[name="firstname"]').val().trim();
    const email = $form.find('input[name="email"]').val().trim();
    const phone = $form.find('input[name="phone"]').val().trim();
    const contactMethod = $form.find('select[name="contact_method"]').val();
    const properties = $form.find('select[name="properties"]').val();
    const adminMethod = $form.find('select[name="admin_method"]').val();

    const $btn = $form.find('.btn-send-form');

    if (firstname && email && phone && contactMethod !== '0' && properties !== '0' && adminMethod !== '0') {
      $btn.removeClass('disabled-btn');
    } else {
      $btn.addClass('disabled-btn');
    }
  }

  $('#form-contact').on('input change', 'input, textarea, select', function () {
    checkContactFormFields();
  });

  $('#form-contact').on('click', '.custom-option', function () {
    setTimeout(checkContactFormFields, 50);
  });

  checkContactFormFields();

  $('.input-digits-only').on('input', function () {
    this.value = this.value.replace(/[^0-9]/g, '');
    if (this.value.length > 10) this.value = this.value.slice(0, 10);
  });

  $.validator.addMethod("domain", function (value, element) {
    return this.optional(element) || /\.[a-zA-Z]{2,}$/.test(value);
  }, "Dominio inválido");

  jQuery.validator.addMethod("notDefault", function (value, element) {
    return value !== "0" && value !== "";
  }, "Selecciona una opción");

  const commonHighlight = function (element) {
    const $el = $(element);
    if ($el.is("select")) {
      $el.siblings(".custom-select-container").find(".custom-select-trigger").addClass("error");
      $el.closest("div").find(".info-error").removeClass("d-none");
    } else {
      $el.addClass("error").removeClass("valid");
      $el.closest("div").find(".info-error").removeClass("d-none");
    }
  };

  const commonUnhighlight = function (element) {
    const $el = $(element);
    if ($el.is("select")) {
      $el.siblings(".custom-select-container").find(".custom-select-trigger").removeClass("error");
      $el.closest("div").find(".info-error").addClass("d-none");
    } else {
      $el.removeClass("error").addClass("valid");
      $el.closest("div").find(".info-error").addClass("d-none");
    }
  };

  const commonErrorPlacement = function (error, element) {
    return false;
  };

  const commonSuccess = function (label, element) {
    const $el = $(element);
    $el.closest("div").find(".info-error").addClass("d-none");
  };

  $("#form-contact").validate({
    ignore: [],
    rules: {
      firstname: { required: true, minlength: 3 },
      email: { required: true, email: true, domain: true },
      phone: { required: true, digits: true, minlength: 10, maxlength: 10 },
      contact_method: { required: true, notDefault: true },
      properties: { required: true, notDefault: true },
      admin_method: { required: true, notDefault: true },
      message: { required: false, minlength: 10 }
    },
    messages: {
      firstname: { required: "Introduce tu nombre", minlength: "El nombre debe tener al menos 3 caracteres" },
      email: { required: "Introduce una cuenta de correo válida", email: "Introduce una cuenta de correo válida", domain: "Introduce una cuenta de correo válida" },
      phone: { required: "Introduce un número de 10 dígitos", digits: "Introduce un número de 10 dígitos", minlength: "Introduce un número de 10 dígitos", maxlength: "Introduce un número de 10 dígitos" },
      contact_method: { required: "Selecciona una opción", notDefault: "Selecciona una opción" },
      properties: { required: "Selecciona una opción", notDefault: "Selecciona una opción" },
      admin_method: { required: "Selecciona una opción", notDefault: "Selecciona una opción" },
      message: { minlength: "Necesitamos un poco más de información para ayudarte" }
    },
    highlight: commonHighlight,
    unhighlight: commonUnhighlight,
    errorPlacement: commonErrorPlacement,
    success: commonSuccess
  });

  $(".custom-option").on("click", function () {
    const value = $(this).data("value");
    const $container = $(this).closest('.custom-select-container');
    const $select = $container.prev('select');

    $select.val(value).trigger("change");
    $select.valid();
    $container.find(".custom-select-trigger").removeClass("error");
  });

  $(".btn-send-form a").on('click', function (e) {
    e.preventDefault();
    const $form = $(this).closest("form");
    if ($form.length === 0) return;

    const honeypot = $form.find('input[name="check_bot_field"]').val();
    if (honeypot && honeypot.length > 0) return false;

    if (!$form.valid()) {
      $form.validate().focusInvalid();
      return;
    }

    const $btnContainer = $form.find('.btn-send-form');
    const $btnText = $btnContainer.find('span');
    const originalText = $btnText.text();

    $btnContainer.addClass('disabled-btn');
    $btnText.text("Enviando...");

    const formData = $form.serializeArray();

    $.ajax({
      url: SCRIPT_URL,
      type: "POST",
      data: $.param(formData),
      success: function (response) {
        if (response.trim() === "SUCCESS") {
          window.location.href = "gracias.html";
        } else {
          alert("Error al enviar. Intenta de nuevo.\nRespuesta: " + response);
          $btnContainer.removeClass('disabled-btn');
          $btnText.text(originalText);
        }
      },
      error: function (xhr, status, error) {
        alert("Error de conexión: " + error);
        $btnContainer.removeClass('disabled-btn');
        $btnText.text(originalText);
      }
    });
  });

});



var swiperCol4 = new Swiper(".swiperColFour", {
  slidesPerView: 1.5,
  spaceBetween: 16,
  slidesOffsetBefore: 16,
  slidesOffsetAfter: 16,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  breakpoints: {
    640: {
      slidesPerView: 1.5,
      spaceBetween: 16,
      slidesOffsetBefore: 16,
      slidesOffsetAfter: 16,
    },
    768: {
      slidesPerView: 3,
      spaceBetween: 20,
      slidesOffsetBefore: 0,
      slidesOffsetAfter: 0,
    },
    1024: {
      slidesPerView: 4,
      spaceBetween: 21,
      slidesOffsetBefore: 0,
      slidesOffsetAfter: 0,
    },
  },
});

var swiperPlans = new Swiper(".swiperPlans", {
  slidesPerView: 1.2,
  spaceBetween: 8,
  slidesOffsetBefore: 16,
  slidesOffsetAfter: 16,
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
  },
  breakpoints: {
    640: {
      slidesPerView: 1.2,
      spaceBetween: 8,
      slidesOffsetBefore: 16,
      slidesOffsetAfter: 16,
    },
    768: {
      slidesPerView: 2,
      spaceBetween: 17,
      slidesOffsetBefore: 0,
      slidesOffsetAfter: 0,
    },
    1024: {
      slidesPerView: 2,
      spaceBetween: 17,
      slidesOffsetBefore: 0,
      slidesOffsetAfter: 0,
    },
  },
});
swiperPlans.slides.forEach(slide => {
  slide.addEventListener('click', function (e) {
    if (swiperPlans.clickedSlide === this) {
      e.preventDefault();
      const slideUrl = this.getAttribute('data-slide-url');
      if (slideUrl) {
        window.location.href = slideUrl;
      } else {
      }
    }
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const options = { threshold: 0.3 };

  const scrollObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('active');
      } else {
        entry.target.classList.remove('active');
      }
    });
  }, options);

  const scrollElements = document.querySelectorAll(
    '.slide-btn-in-bottom, .fade-in-left, .scale-in-center, .slide-in-left, .slide-in-left-seq, .slide-in-bottom, .slide-in-bottom-seq, .slide-in-bottom-m, .hero-img-item, .slide-in-left-row, .slide-in-left-seq-desk'
  );
  scrollElements.forEach(el => scrollObserver.observe(el));

  function initCustomSelect(wrapperId, selectId) {
    const customSelect = document.getElementById(wrapperId);
    if (customSelect) {
      const trigger = customSelect.querySelector('.custom-select-trigger');
      const options = customSelect.querySelectorAll('.custom-option');
      const hiddenSelect = document.getElementById(selectId);

      trigger.addEventListener('click', () => {
        customSelect.classList.toggle('open');
      });

      options.forEach(option => {
        option.addEventListener('click', function () {
          const value = this.getAttribute('data-value');
          const text = this.textContent;

          trigger.textContent = text;
          trigger.classList.add('selected');

          hiddenSelect.value = value;

          options.forEach(opt => opt.classList.remove('selected'));
          this.classList.add('selected');

          customSelect.classList.remove('open');
        });
      });

      document.addEventListener('click', function (e) {
        if (!customSelect.contains(e.target)) {
          customSelect.classList.remove('open');
        }
      });
    }
  }

  initCustomSelect('custom-contact-method', 'contact_method');
  initCustomSelect('custom-properties', 'properties');
  initCustomSelect('custom-admin-method', 'admin_method');
});
document.addEventListener('DOMContentLoaded', () => {
  const DEFAULT_OFFSET_SM = 40;
  const DEFAULT_OFFSET_LG = 20;
  const MOBILE_BREAKPOINT = 768;


  const calculateOffset = (anchor) => {
    const isMobile = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT}px)`).matches;

    const offsetSmall = parseInt(anchor.getAttribute('data-offset-s'));
    const offsetLarge = parseInt(anchor.getAttribute('data-offset-l'));

    let offset = isMobile
      ? (isNaN(offsetSmall) ? DEFAULT_OFFSET_SM : offsetSmall)
      : (isNaN(offsetLarge) ? DEFAULT_OFFSET_LG : offsetLarge);

    if (anchor.getAttribute('href') === '#contact') {
      const customOffsetProvided = isMobile
        ? !isNaN(offsetSmall)
        : !isNaN(offsetLarge);

      if (!customOffsetProvided) {
        offset = isMobile ? DEFAULT_OFFSET_SM : DEFAULT_OFFSET_LG;
      }
    }

    return offset;
  };

  const closeNavbarCollapse = (anchor) => {
    const navbarCollapse = document.getElementById('navbarMainMenu');
    if (!navbarCollapse || !navbarCollapse.classList.contains('show')) return;
    if (navbarCollapse.contains(anchor)) {
      if (typeof bootstrap !== 'undefined' && bootstrap.Collapse) {
        const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
        if (bsCollapse) {
          bsCollapse.hide();
        } else {
          new bootstrap.Collapse(navbarCollapse, { toggle: false }).hide();
        }
      }
    }
  };
  const incomingHash = window.location.hash;

  if (incomingHash) {
    const target = document.querySelector(incomingHash);

    if (target) {
      const mockAnchor = {
        getAttribute: (attr) => {
          if (attr === 'href') return incomingHash;
          return null;
        }
      };

      const offset = calculateOffset(mockAnchor);
      setTimeout(() => {
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }, 10);

      if (window.history.replaceState) {
        window.history.replaceState(null, null, window.location.pathname);
      }
    }
  }
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId.length > 1) {
        e.preventDefault();
        const target = document.querySelector(targetId);
        if (!target) return;
        const offset = calculateOffset(this);
        closeNavbarCollapse(this);
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // Automatiza tabs - hover to switch
  var triggerTabList = document.querySelectorAll('#v-pills-automatiza-tab button.nav-link');
  triggerTabList.forEach(function (triggerEl) {
    triggerEl.addEventListener('mouseenter', function (event) {
      var tabTrigger = new bootstrap.Tab(triggerEl);
      tabTrigger.show();
    });
  });
});
