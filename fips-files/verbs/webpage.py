"""fips verb to build the samples webpage"""

import os
import yaml
import shutil
import subprocess
import glob
from string import Template

from mod import log, util, project

# webpage template arguments
GitHubSamplesURL = 'https://github.com/floooh/sokol-samples/tree/master/sapp/'

# webpage text colors
Keys = {
    'webgl': {
        'title': 'Sokol WebGL',
        'cross_name': 'webgpu',
        'cross_url': 'https://floooh.github.io/sokol-webgpu',
        'body_bg_color': '#292d3e',
        'thumb_bg_color': '#4a4d62',
        'text_color': '#1ABC9C',
    },
    'webgpu': {
        'title': 'Sokol WebGPU',
        'cross_name': 'webgl',
        'cross_url': 'https://floooh.github.io/sokol-html5',
        'body_bg_color': '#292d3e',
        'thumb_bg_color': '#4a4d62',
        'text_color': '#3498DB',
    }
}

# build configuration
def get_build_config(api):
    if api == 'webgl':
        return 'sapp-webgl2-wasm-ninja-release'
    else:
        return 'sapp-wgpu-wasm-ninja-release'

# sample attributes
samples = [
    [ 'sdf', 'sdf-sapp.c', 'sdf-sapp.glsl'],
]

# assets that must also be copied
assets = [
]

#-------------------------------------------------------------------------------
def deploy_webpage(fips_dir, proj_dir, api, webpage_dir) :
    wasm_deploy_dir = util.get_deploy_dir(fips_dir, 'sokol-samples', get_build_config(api))

    # build the thumbnail gallery
    content = ''
    for sample in samples:
        name = sample[0]
        log.info('> adding thumbnail for {}'.format(name))
        url = "{}-sapp.html".format(name)
        ui_url = "{}-sapp-ui.html".format(name)
        img_name = name + '.jpg'
        img_path = proj_dir + '/webpage/' + img_name
        if not os.path.exists(img_path):
            img_name = 'dummy.jpg'
            img_path = proj_dir + 'webpage/dummy.jpg'
        content += '<div class="thumb">'
        content += '  <div class="thumb-title">{}</div>'.format(name)
        if os.path.exists(wasm_deploy_dir + '/' + name + '-sapp-ui.js'):
            content += '<a class="img-btn-link" href="{}"><div class="img-btn">UI</div></a>'.format(ui_url)
        content += '  <div class="img-frame"><a href="{}"><img class="image" src="{}"></img></a></div>'.format(url,img_name)
        content += '</div>\n'

    # populate the html template, and write to the build directory
    with open(proj_dir + '/webpage/index.html', 'r') as f:
        templ = Template(f.read())
    keys = Keys[api]
    html = templ.safe_substitute(
        samples = content,
        title = keys['title'],
        cross_name = keys['cross_name'],
        cross_url = keys['cross_url'],
        body_bg_color = keys['body_bg_color'],
        thumb_bg_color = keys['thumb_bg_color'],
        text_color = keys['text_color'])

    with open(webpage_dir + '/index.html', 'w') as f :
        f.write(html)

    # copy other required files
    for name in ['dummy.jpg', 'favicon.png']:
        log.info('> copy file: {}'.format(name))
        shutil.copy(proj_dir + '/webpage/' + name, webpage_dir + '/' + name)

    # generate WebAssembly HTML pages
    for sample in samples :
        name = sample[0]
        source = sample[1]
        glsl = sample[2]
        log.info('> generate wasm HTML page: {}'.format(name))
        for postfix in ['sapp', 'sapp-ui']:
            for ext in ['wasm', 'js'] :
                src_path = '{}/{}-{}.{}'.format(wasm_deploy_dir, name, postfix, ext)
                if os.path.isfile(src_path) :
                    shutil.copy(src_path, '{}/'.format(webpage_dir))
                with open(proj_dir + '/webpage/wasm.html', 'r') as f :
                    templ = Template(f.read())
                src_url = GitHubSamplesURL + source
                if glsl is None:
                    glsl_url = "."
                    glsl_hidden = "hidden"
                else:
                    glsl_url = GitHubSamplesURL + glsl
                    glsl_hidden = ""
                html = templ.safe_substitute(name=name, prog=name+'-'+postfix, source=src_url, glsl=glsl_url, hidden=glsl_hidden)
                with open('{}/{}-{}.html'.format(webpage_dir, name, postfix), 'w') as f :
                    f.write(html)

    # copy assets from deploy directory
    for asset in assets:
        log.info('> copy asset file: {}'.format(asset))
        src_path = '{}/{}'.format(wasm_deploy_dir, asset)
        if os.path.isfile(src_path):
            shutil.copy(src_path, webpage_dir)
        else:
            log.warn('!!! file {} not found!'.format(src_path))

    # copy the screenshots
    for sample in samples :
        img_name = sample[0] + '.jpg'
        img_path = proj_dir + '/webpage/' + img_name
        if os.path.exists(img_path):
            log.info('> copy screenshot: {}'.format(img_name))
            shutil.copy(img_path, webpage_dir + '/' + img_name)

#-------------------------------------------------------------------------------
def build_deploy_webpage(fips_dir, proj_dir, api, rebuild) :
    # if webpage dir exists, clear it first
    build_config = get_build_config(api)
    proj_build_dir = util.get_deploy_root_dir(fips_dir, 'sokol-samples')
    webpage_dir = '{}/sokol-webpage-{}'.format(proj_build_dir, api)
    if rebuild :
        if os.path.isdir(webpage_dir) :
            shutil.rmtree(webpage_dir)
    if not os.path.isdir(webpage_dir) :
        os.makedirs(webpage_dir)

    # compile samples
    project.gen(fips_dir, proj_dir, build_config)
    project.build(fips_dir, proj_dir, build_config)

    # deploy the webpage
    deploy_webpage(fips_dir, proj_dir, api, webpage_dir)

    log.colored(log.GREEN, 'Generated Samples web page under {}.'.format(webpage_dir))

#-------------------------------------------------------------------------------
def serve_webpage(fips_dir, proj_dir, api) :
    proj_build_dir = util.get_deploy_root_dir(fips_dir, 'sokol-samples')
    webpage_dir = '{}/sokol-webpage-{}'.format(proj_build_dir, api)
    p = util.get_host_platform()
    if p == 'osx' :
        try :
            subprocess.call(
                'http-server -c-1 -g -o'.format(fips_dir),
                cwd = webpage_dir, shell=True)
        except KeyboardInterrupt :
            pass
    elif p == 'win':
        try:
            subprocess.call(
                'http-server -c-1 -g -o'.format(fips_dir),
                cwd = webpage_dir, shell=True)
        except KeyboardInterrupt:
            pass
    elif p == 'linux':
        try:
            subprocess.call(
                'http-server -c-1 -g -o'.format(fips_dir),
                cwd = webpage_dir, shell=True)
        except KeyboardInterrupt:
            pass

#-------------------------------------------------------------------------------
def run(fips_dir, proj_dir, args) :
    if len(args) > 0 :
        action = args[0]
        api = 'webgl'
        if len(args) > 1:
            api = args[1]
        if api not in ['webgl', 'webgpu']:
            log.error("Invalid param '{}', expected 'webgl' or 'webgpu'".format(api))
        if action == 'build' :
            build_deploy_webpage(fips_dir, proj_dir, api, False)
        elif action == 'rebuild' :
            build_deploy_webpage(fips_dir, proj_dir, api,  True)
        elif action == 'serve' :
            serve_webpage(fips_dir, proj_dir, api)
        else :
            log.error("Invalid param '{}', expected 'build' or 'serve'".format(action))
    else :
        log.error("Params 'build|rebuild|serve [webgl|webgpu]' expected")

#-------------------------------------------------------------------------------
def help() :
    log.info(log.YELLOW +
             'fips webpage build [webgl|webgpu]\n' +
             'fips webpage rebuild [webgl|webgpu]\n' +
             'fips webpage serve [webgl|webgpu]\n' +
             log.DEF +
             '    build sokol samples webpage')
