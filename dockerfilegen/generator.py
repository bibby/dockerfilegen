import os
import jinja2
import re


class Dockerfile():
    """kwargs - see README.md"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.jinja = jinja2.Environment(loader=jinja2.FileSystemLoader([os.path.dirname(__file__) + '/tpls', self.tpl_path]),
            extensions=['jinja2.ext.autoescape'], autoescape=False)

    def render(self):
        """generate dockerfiles and shell script"""
        self.validate()
        generated_files = self.generate_dockerfiles()
        self.generate_build_script(generated_files)

    def generate_dockerfiles(self):
        """generate all the image variations described in the tree"""
        generated_files = []
        for base in self.bases:
            generated_files.append(self.generate_dockerfile(**base))
        return generated_files

    def generate_dockerfile(self, base=None, tag=None, template=None):
        """generates a dockerfile from a unique base image"""
        template_vars = {
            "base": base,
            "maintainer": getattr(self, "maintainer", None)
        }
        output_filename = os.path.join(self.out_path, tag + ".docker")
        jinja_template = self.jinja.get_template(template)
        with open(output_filename, "w") as output_file:
            output_file.write(self.clean_text(jinja_template.render(template_vars)))

        print "generated dockerfile: {}".format(output_filename)
        return {
            "dockerfile": output_filename,
            "image": self.image_name,
            "tag": tag,
            "base": base
        }

    def generate_build_script(self, generated_files):
        """generates a shell script to build all the docker images in sequence"""
        build_script_tpl = getattr(self, "build_script_tpl", "default_build_script.j2")
        script_template = self.jinja.get_template(build_script_tpl)
        script_filename = os.path.join(self.out_path, "build.sh")
        with open(script_filename, "w") as script_file:
            script = script_template.render(
                generated_files=generated_files,
                path=self.src_path,
                tag_registry=getattr(self, "tag_registry", None),
                push=getattr(self, "push", False)
            )
            script_file.write(self.clean_text(script))

        os.chmod(script_filename, 0755)
        print "generated build script: {}".format(script_filename)

    def validate(self):
        """tests input vars for correctness-ish"""
        if not self.image_name:
            raise Exception("image_name not specified. Expected string: myimage, my/image, registry:1234/my/image")

        if not os.path.isdir(self.tpl_path):
            raise Exception("tpl_path not a directory: requires a path to locate template files")

        self.out_path = self.out_path or "build"
        if not os.path.exists(self.out_path):
            os.mkdir(self.out_path)

        if not os.path.isdir(self.out_path):
            raise Exception("out_path not a directory: {}\nSpecify out_path as a directory to use or to create".format(
                self.out_path))

        if not self.bases:
            raise Exception("tree not defined. So nothing to build.")

        if not self.src_path:
            self.src_path = '.'
        if not os.path.isdir(self.src_path):
            raise Exception("src_path not a directory: {}\nSpecify src_path as a directory ".format(self.src_path))

    def clean_text(self, text):
        """removes spacing over two lines long"""
        return re.sub("\n\n\n+", "\n\n", text)