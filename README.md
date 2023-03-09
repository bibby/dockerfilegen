# dockerfilegen

More specifically, a dockerfile multi-baser. Uses jinja2 templates to cobble together several dockerfiles using a different base for each; because inheritance.

This can be useful if you have a particular library that would want to have built upon multiple OS versions.

## sample project

_structure_

    myproject/
        tpls/
            ubuntu.j2
            centos_6.j2
        myapp.py
        docker-gen.py

Create a _plain-old_ python file to describe your image, and the parent images you want it based from, in this case, `docker-gen.py`

_docker-gen.py_

    import os
    from dockerfilegen.generator import Dockerfile

    bases = [
        {
            "base": "registry:5000/base/ubuntu:14.04.2",
            "tag": "ubuntu.14.04.2",
            "template": "ubuntu.j2"
        },
        {
            "base": "registry:5000/base/centos:6",
            "tag": "centos.6",
            "template": "centos.j2"
        }
    ]


    Dockerfile(
        image_name="myname/myapp",
        bases=bases,
        tpl_path="tpls",
        out_path="build",
        src_path=os.path.dirname(__file__)
    ).render()

_a run_

    $ python docker-gen.py                                                                                                        
    generated dockerfile: build/centos_6.docker
    generated dockerfile: build/ubuntu_14.04.2.docker
    generated build script: build/build.sh


## params

The `bases` element is a list of *image-dicts*, each with three items:

* `base` - the name of the docker image to inherit from
* `tag` - the tag of the final image when built
* `template` - the local jinja2 template to use

`image_name` will be the name of the image that these docker files would build, as named in the shell script that is also generated. If you have a registry to add here, you may; it is just a string.

`tpl_path` is the location of this project's internal templates -- more on those below.

`out_path` is the location where this module should write its output docker files and build script.

`src_path` is the location of the project sources that should be included in the build script; the location for docker to build from. Using a full path is recommended to be able to invoke the build script from anywhere.

`maintainer` optional dockerfile maintainer string, excluding the literal "MAINTAINER"

`build_script_tpl` optional local template to override the build.sh template

`tag_registry` optional string of a registry. If used a `docker tag` call is made.

`push` optional boolean to push a tagged image to the `tag_registry` if it is defined.

## templates

The docker files are based from a common jinja2 template (Dockerfile.j2),
which is little more than empty blocks.
The bulk of the docker file content will be provided by your project.
These are the named blocks in the order in which they appear in the base template:

    first
    env
    volume
    pre_procedure
    procedure
    post_procedure
    cmd
    last

Not all blocks must be filled; just use what makes sense to you.
Also don't worry about an overabundance of empty lines; the output will get slimmed down.
