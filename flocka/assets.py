from flask_assets import Bundle

common_css = Bundle(
    'css/vendor/bootstrap.min.css',
    'css/vendor/helper.css',
    'css/main.css',
    filters='cssmin',
    output='public/css/common.css'
)

common_js = Bundle(
    'vendor/jquery.min.js',
    'vendor/bootstrap.min.js',
    'vendor/jquery.pjax.js',
    'vendor/spin.js',
    'vendor/jquery.spin.js',
    'vendor/pjax-table/js/pjax_table.min.js',
    Bundle(
        'js/main.js',
        filters='jsmin'
    ),
    output='public/js/common.js'
)
