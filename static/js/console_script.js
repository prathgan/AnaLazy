// Focus & Set Version
jQuery('.console-input').focus();
var ver = "3.5";
jQuery('#ver').html(ver);

// Force Lowercase Input
jQuery('.console-input').keyup(function() {
  //this.value = this.value.toLowerCase();
});

// Force Cursor to End
jQuery('.console-input').keydown(function() {
  this.value = this.value;
});
jQuery('.console-input').click(function() {
  this.value = this.value;
});

// Output to Console
function output(print) {
  var cmd = jQuery('.console-input').val();
  if(cmd==""){cmd="<span style='opacity:0;'>...</span>";}
  jQuery("#outputs").append("<span class='output-cmd-pre'>In ></span><span class='output-cmd'>" + cmd + "</span>");

  jQuery.each(print, function(index, value) {
    cmd = "Out";
    cmd += " >";
    if (value == "") {
      value = "&nbsp;";
    }
    jQuery("#outputs").append("<span class='output-text-pre'>" + cmd + "</span><span class='output-text'>" + value + "</span>");
  });
  
  jQuery('.console-input').val("");
  //jQuery('.console-input').focus();
  jQuery("html, body").animate({
    scrollTop: jQuery(document).height()
  }, 300);
}

// Break Value
var newLine = "<br/> &nbsp;";

// User Commands
var cmds = {
  
  "/load_csv": function() {
    // load_csv function
  },

  
  "/reset": function() {
    window.location.replace(location.href);
  },

  "/alert": function(a) {
    alert(a);
    output([]);
  },

  "/geturl": function(a) {
    var print = [];
    print.push("GETURL > URL request sent");
    jQuery.ajax({
      url: a,
      type: 'GET',
      success: function(data) { 
        print.push("GETURL > Begin return ouput");
        print.push(data.replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/(?:\r\n|\r|\n)/g, '<br />').replace(/\t/g, '&nbsp;&nbsp;'));
        print.push("GETURL > End return ouput")
        output(print);
      },
      error: function(data, status, error)  {
        print.push("GETURL > Unable to load URL");
        output(print);
      }
    });
  },
  
  "/js": function(str) {
    var print = [];
    print.push("JS > Input Run");
    try {
      (new Function(str))();
      print.push("JS > Code Executed Successfully");
    } catch(err) {
      print.push("JS > Code Error: " + err.message);
    }
    output(print);
  },

  "/clear": function() {
    jQuery("#outputs").html("");
  },

  "/help": function() {

    var print = ["Commands:", ""];
    print = jQuery.merge(print, Object.keys(cmds));

    output(print);
  },

  "/contact": function() {

    var print = [
      "Contact Me:",
      "",
      "Email: <span>pratham@uchicago.edu</span>",
      "Twitter: <span>@prathgan</span>",
      "GitHub: <span>prathgan</span>"
    ];

    output(print);
  },

};

// Output Branding
//jQuery('.console-input').val("Loading...");



// Get User Command
jQuery('.console-input').on('keypress', function(event) {
  if (event.which === 13) {
    var str = jQuery(this).val();
    var data = str.split(' '); data.shift(); data = data.join(' ');
    var cmd = str.split(' ')[0];
    
    if (typeof cmds[cmd] == 'function') {
      if(cmds[cmd].length > 0) {
        cmds[cmd](data);
      } else {
        cmds[cmd]();
      }
    // } else if ( (str.slice(0, str.indexOf('(')) === 'function' && str.slice(-1) === '}') || typeof eval(str.slice(0, str.indexOf('('))) === 'function') {
    //   var print = [];
    //   print.push("JS Direct Code Input Run");
    //   if(str.slice(0, str.indexOf('(')) === 'function') { str = str.replace('function(){', '').slice(0, -1); }
    //   try {
    //     (new Function(str))();
    //   } catch(err) {
    //     print.push("JS Direct Code Error: " + err.message);
    //   }
    //   output(print);
    } else {
      output(["Command not found: '" + cmd + "'", "Use '/help' for list of commands."]);
    }
    jQuery(this).val("");
  }
});

// Particles BG
/*
particlesJS('particles-js', {
  'particles': {
    'number': {
      'value': 50
    },
    'color': {
      'value': '#ffffff'
    },
    'shape': {
      'type': 'triangle',
      'polygon': {
        'nb_sides': 5
      }
    },
    'opacity': {
      'value': 0.06,
      'random': false
    },
    'size': {
      'value': 11,
      'random': true
    },
    'line_linked': {
      'enable': true,
      'distance': 150,
      'color': '#ffffff',
      'opacity': 0.4,
      'width': 1
    },
    'move': {
      'enable': true,
      'speed': 4,
      'direction': 'none',
      'random': false,
      'straight': false,
      'out_mode': 'out',
      'bounce': false
    }
  },
  'interactivity': {
    'detect_on': 'canvas',
    'events': {
      'onhover': {
        'enable': false
      },
      'onclick': {
        'enable': true,
        'mode': 'push'
      },
      'resize': true
    },
    'modes': {
      'push': {
        'particles_nb': 4
      }
    }
  },
  'retina_detect': true
}, function() {

});
*/
